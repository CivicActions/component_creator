# mypy: ignore-errors
import json
import logging
from pathlib import Path
from typing import List, Literal, Optional, Union

from pydantic import (  # pylint: disable=no-name-in-module
    UUID4,
    BaseModel,
    ValidationError,
    validator,
)

from app.oscal.oscal import (
    BackMatter,
    Link,
    Metadata,
    OSCALElement,
    Parameter,
    Property,
)

logger = logging.getLogger(__name__)


class BaseControl(OSCALElement):
    class Meta:
        fields = {"item_class": "class"}
        allow_population_by_field_name = True

    id: str
    item_class: Optional[str]
    title: str
    params: Optional[List[Parameter]] = []
    props: Optional[List[Property]] = []
    links: Optional[List[Link]] = []


# noinspection PyUnresolvedReferences
class FilterMixin:
    def _filter_list_field(self, key: str, field: str):
        return next(filter(lambda item_: item_.name == key, getattr(self, field)), None)

    def _get_prop(self, key: str) -> "Property":
        return self._filter_list_field(key, field="props")

    def _get_part(self, key: str) -> "Part":
        return self._filter_list_field(key, field="parts")

    @property
    def label(self) -> str:
        prop = self._get_prop("label")

        if not prop:
            return self.id

        return prop.value


class Part(BaseModel, FilterMixin):
    id: Optional[str]
    name: str
    props: Optional[List[Property]] = []
    parts: Optional[List["Part"]] = []
    prose: Optional[str] = ""


class Control(BaseControl, FilterMixin):
    class Config:
        fields = {"family_id": "id"}
        allow_population_by_field_name = True

    family_id: Optional[str]
    parts: Optional[List[Part]] = []
    controls: Optional[List["Control"]] = []

    @property
    def sort_id(self) -> str:
        prop = self._get_prop("sort-id")

        if not prop:
            return self.title

        return prop.value

    @property
    def statement(self) -> List:
        statements_list: List = []
        statement = self._get_part("statement")
        if prose := getattr(statement, "prose", False):
            label = next(
                filter(
                    lambda item_: item_.name == "label", getattr(statement, "props")
                ),
                None,
            )
            statements_list.append(
                {
                    "id": getattr(statement, "id"),
                    "prose": prose,
                    "label": label,
                }
            )
        if parts := getattr(statement, "parts", []):
            statements_list = self._get_flat_parts(parts, statements_list)

        return statements_list

    def _get_flat_parts(self, parts, statement_list):
        for part in parts:
            if prose := getattr(part, "prose", False):
                label = next(
                    filter(lambda item_: item_.name == "label", getattr(part, "props")),
                    None,
                )
                statement_list.append(
                    {
                        "id": getattr(part, "id"),
                        "prose": prose,
                        "label": label,
                    }
                )
            if subpart := getattr(part, "parts", False):
                self._get_flat_parts(subpart, statement_list)
        return statement_list

    @property
    def implementation(self) -> Optional[str]:
        part = self._get_part("implementation")

        if not part:
            return ""

        return part.prose

    @property
    def guidance(self) -> Optional[str]:
        part = self._get_part("guidance")

        if not part:
            return ""

        return part.prose

    @property
    def parameters(self) -> dict:
        params = self.params
        parameters = {}
        for p in params:
            parameters[p.id] = p.get_odp_text
        return parameters

    def get_links(self) -> dict:
        links_list: dict = {
            "reference": [],
            "related": [],
        }
        if links := getattr(self, "links"):
            for link in links:
                rel = link.rel
                href = link.href[1:]
                if rel == "reference":
                    resource = links.__get_resource_by_uuid(href)
                    links_list["reference"].append(resource)
                elif rel == "related":
                    links_list["related"].append(href)
        return links_list

    def to_orm(self) -> dict:
        return {
            "control_id": self.id,
            "control_label": self.label,
            "sort_id": self.sort_id,
            "title": self.title,
        }


class Group(OSCALElement):
    class Config:
        fields = {"item_class": "class"}
        allow_population_by_field_name = True

    id: Optional[str]
    item_class: Literal["family"]
    title: str
    params: Optional[List[Parameter]] = []
    props: Optional[List[Property]] = []
    parts: Optional[List["Part"]] = []
    groups: Optional[List["Group"]]
    controls: Optional[List[Control]]

    @validator("controls")
    def set_family_id(
        cls, value: List[Control], values
    ) -> List[Control]:  # pylint: disable=no-self-argument
        for item in value:
            if not item.title:
                item.family_id = values.get("id")

        return value


class CatalogModel(BaseModel):
    class Config:
        fields = {"back_matter": "back-matter"}
        allow_population_by_field_name = True

    uuid: UUID4
    metadata: Metadata
    groups: Optional[List[Group]]
    controls: Optional[List[Control]]
    back_matter: Optional[BackMatter]

    @property
    def controls(self) -> List[Control]:
        controls = []
        for group in self.groups:
            for item in getattr(group, "controls"):
                controls.append(item)
                if children := getattr(item, "controls", ""):
                    for ctrl in children:
                        controls.append(ctrl)
        return controls

    def get_control(self, control_id: str) -> Optional[Control]:
        return next(
            filter(lambda control: control.id == control_id, self.controls), None
        )

    def get_groups(self) -> List:
        groups_list: List = []
        groups = getattr(self, "groups")
        for group in groups:
            control_list = []
            if controls := getattr(group, "controls"):
                control_list = self.get_group_controls(controls)
            groups_list.append(
                {
                    "group_id": group.id,
                    "title": group.title,
                    "controls": control_list,
                }
            )

        return groups_list

    def get_group_controls(self, controls: List) -> List:
        control_list = []
        for control in controls:
            temp_control = {
                "control_id": control.id,
                "title": control.title,
            }
            if enhancements := getattr(control, "controls"):
                temp_control["enhancements"] = self.get_group_controls(enhancements)
            control_list.append(temp_control)
        return control_list

    def get_group(self, control_id: str) -> List[Group]:
        for group in self.groups:
            for control in group.controls:
                if control.id == control_id:
                    return group
                elif children := getattr(control, "controls", ""):
                    for child in children:
                        if child.id == control_id:
                            return group

    def get_next(self, control: Control) -> str:
        try:
            next_idx = self.controls.index(control) + 1
            return self.controls[next_idx].id
        except (ValueError, IndexError):
            return ""

    def control_summary(self, control_id: str) -> dict:
        control = self.get_control(control_id)
        group = self.get_group(control_id)
        next_id = self.get_next(control)

        return {
            "label": control.label,
            "sort_id": control.sort_id,
            "title": control.title,
            "family": group.title,
            "description": control.description,
            "implementation": control.implementation,
            "guidance": control.guidance,
            "next_id": next_id,
        }

    @classmethod
    def from_json(cls, json_file: Union[str, Path]):
        with open(json_file, "rb") as file:
            data = json.load(file)

        try:
            return cls(**data)
        except ValidationError:  # Try nested "catalog" field
            return cls(**data["catalog"])
