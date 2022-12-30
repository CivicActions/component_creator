import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

OSCAL_VERSION = "1.0.0"


class ControlRegExps:
    nist_800_171 = re.compile(r"^\d+\.\d+(\.\d+)*$")
    nist_800_53_simple = re.compile(r"^([a-z]{2})-(\d+)$")
    nist_800_53_extended = re.compile(r"^([a-z]{2})-(\d+)\s*\((\d+)\)$")
    nist_800_53_part = re.compile(r"^([a-z]{2})-(\d+)\.([a-z]+)$")
    nist_800_53_extended_part = re.compile(r"^([a-z]{2})-(\d+)\s*\((\d+)\)\.([a-z]+)$")


def oscalize_control_id(control_id):
    """
    output an oscal standard control id from various common formats for control ids
    """

    control_id = control_id.strip()
    control_id = control_id.lower()

    # 1.2, 1.2.3, 1.2.3.4, etc.
    if re.match(ControlRegExps.nist_800_171, control_id):
        return control_id

    # AC-1
    match = re.match(ControlRegExps.nist_800_53_simple, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        return f"{family}-{number}"

    # AC-2(1)
    match = re.match(ControlRegExps.nist_800_53_extended, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        extension = int(match.group(3))
        return f"{family}-{number}.{extension}"

    # AC-1.a
    match = re.match(ControlRegExps.nist_800_53_part, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        return f"{family}-{number}"

    # AC-2(1).b
    match = re.match(ControlRegExps.nist_800_53_extended_part, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        extension = int(match.group(3))
        return f"{family}-{number}.{extension}"

    return control_id


def control_to_statement_id(control_id):
    """
    Construct an OSCAL style statement ID from a control identifier.
    """

    control_id = control_id.strip()
    control_id = control_id.lower()

    # 1.2, 1.2.3, 1.2.3.4, etc.
    if re.match(ControlRegExps.nist_800_171, control_id):
        return f"{control_id}_smt"

    # AC-1
    match = re.match(ControlRegExps.nist_800_53_simple, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        return f"{family}-{number}_smt"

    # AC-2(1)
    match = re.match(ControlRegExps.nist_800_53_extended, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        extension = int(match.group(3))
        return f"{family}-{number}.{extension}_smt"

    # AC-1.a
    match = re.match(ControlRegExps.nist_800_53_part, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        part = match.group(3)
        return f"{family}-{number}_smt.{part}"

    # AC-2(1).b
    match = re.match(ControlRegExps.nist_800_53_extended_part, control_id)
    if match:
        family = match.group(1)
        number = int(match.group(2))
        extension = int(match.group(3))
        part = match.group(4)
        return f"{family}-{number}.{extension}_smt.{part}"

    # nothing matched ...
    return f"{control_id}_smt"


class NCName(str):
    pass


class MarkupLine(str):
    pass


class MarkupMultiLine(str):
    pass


class OSCALElement(BaseModel):
    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        if hasattr(self.Config, "container_assigned"):
            for key in self.Config.container_assigned:
                if key in d:
                    del d[key]
        if hasattr(self.Config, "exclude_if_false"):
            for key in self.Config.exclude_if_false:
                if not d.get(key, False) and key in d:
                    del d[key]
        return d


class Property(OSCALElement):
    class Config:
        fields = {"prop_class": "class"}
        allow_population_by_field_name = True

    name: str
    value: str
    ns: Optional[str]
    uuid: UUID = Field(default_factory=uuid4)
    prop_class: Optional[str]
    remarks: Optional[MarkupMultiLine]


class DocumentId(OSCALElement):
    scheme: Optional[str]
    identifier: Optional[str]

    # missing: annotations, document-ids, citation, rlinks, base64


class LinkRelEnum(str, Enum):
    homepage = "homepage"
    interview_notes = "interview-notes"
    tool_output = "tool-output"
    photograph = "photograph"
    questionnaire = "questionnaire"
    screen_shot = "screen-shot"


class Link(OSCALElement):
    class Config:
        fields = {"media_type": "media-type"}
        allow_population_by_field_name = True

    text: Optional[str]
    href: str
    rel: Optional[str]
    media_type: Optional[str]


class Citation(OSCALElement):
    text: MarkupLine
    props: Optional[List[Property]]
    links: Optional[List[Link]]


class Hash(OSCALElement):
    algorithm: str
    value: Optional[str]


class Rlink(OSCALElement):
    class Config:
        fields = {"media_type": "media-type"}
        allow_population_by_field_name = True

    href: str
    media_type: Optional[str]
    hashes: Optional[List[Hash]]


class Base64(OSCALElement):
    class Config:
        fields = {"media_type": "media-type"}
        allow_population_by_field_name = True

    filename: Optional[str]
    media_type: Optional[str]
    value: Optional[str]


class Resource(OSCALElement):
    class Config:
        fields = {"document_ids": "document-ids", "resource_base64": "base64"}
        allow_population_by_field_name = True

    uuid: UUID = Field(default_factory=uuid4)
    title: Optional[str]
    description: Optional[MarkupMultiLine]
    props: Optional[List[Property]]
    document_ids: Optional[DocumentId]
    citation: Optional[Citation]
    rlinks: Optional[List[Rlink]]
    resource_base64: Optional[Base64]
    remarks: Optional[MarkupMultiLine]


class Annotation(OSCALElement):
    name: NCName
    uuid: Optional[UUID]
    ns: Optional[str]  # really a URI
    value: str
    remarks: Optional[MarkupMultiLine]


class BackMatter(OSCALElement):
    resources: Optional[List[Resource]]

    def get_resource_by_uuid(self, uuid: UUID) -> Union[Resource, Any, None]:
        result = None
        if hasattr(self, "resources"):
            result = next(
                (
                    r
                    for r in self.resources  # type: ignore
                    if hasattr(r, "uuid") and str(r.uuid) == uuid
                ),
                None,
            )
        return result


class EmailAddress(str):
    pass


class TelephoneNumber(OSCALElement):
    type: Optional[str]
    number: str


class Revision(OSCALElement):
    class Config:
        fields = {"last_modified": "last-modified", "oscal_version": "oscal-version"}
        allow_population_by_field_name = True

    title: Optional[str]
    published: Optional[datetime]
    last_modified: Optional[datetime]
    version: Optional[str]
    oscal_version: Optional[str]
    props: Optional[List[Property]]


class PartyTypeEnum(str, Enum):
    person = "person"
    organization = "organization"


class Party(OSCALElement):
    class Config:
        fields = {
            "short_name": "short-name",
            "email_addresses": "email-addresses",
            "telephone-numbers": "telephone-numbers",
        }
        allow_population_by_field_name = True

    uuid: UUID = Field(default_factory=uuid4)
    type: PartyTypeEnum
    name: Optional[str]
    short_name: Optional[str]
    props: Optional[List[Property]]
    annotations: Optional[List[Annotation]]
    links: Optional[List[Link]]
    email_addresses: Optional[List[EmailAddress]]
    telephone_numbers: Optional[List[TelephoneNumber]]
    remarks: Optional[MarkupMultiLine]


class Location(OSCALElement):
    pass


class Test(OSCALElement):
    expression: str
    remarks: Optional[MarkupMultiLine]


class Constraint(OSCALElement):
    description: Optional[MarkupMultiLine]
    tests: Optional[List[Test]]


class Guideline(OSCALElement):
    prose: MarkupMultiLine


class Choice(str):
    choice: Optional[MarkupLine]


class Select(OSCALElement):
    class Config:
        fields = {"how_many": "how-many"}
        allow_population_by_field_name = True

    how_many: Optional[str]
    choice: Optional[List[Choice]]

    @property
    def get_select_text(self):
        text = ""
        if how_many := getattr(self, "how_many", None):
            label = how_many.replace("-", " ")
            text += f"Selection ({label}): "
        if choice := getattr(self, "choice", None):
            ch = []
            [ch.append(c) for c in choice]
            text += ", ".join(ch)
        return text


class RoleIDEnum(str, Enum):
    asset_administrator = "asset-administrator"
    asset_owner = "asset-owner"
    authorizing_official = "authorizing-official"
    authorizing_official_poc = "authorizing-official-poc"
    configuration_management = "configuration-management"
    content_approver = "content-approver"
    help_desk = "help-desk"
    incident_response = "incident-response"
    information_system_security_officer = "information-system-security-officer"
    maintainer = "maintainer"
    network_operations = "network-operations"
    prepared_by = "prepared-by"
    prepared_for = "prepared-for"
    privacy_poc = "privacy-poc"
    provider = "provider"
    security_operations = "security-operations"
    system_owner = "system-owner"
    system_owner_poc_management = "system-owner-poc-management"
    system_owner_poc_other = "system-owner-poc-other"
    system_owner_poc_technical = "system-owner-poc-technical"


class Role(OSCALElement):
    id: str
    title: MarkupLine
    short_name: Optional[str]
    description: Optional[MarkupMultiLine]
    props: Optional[List[Property]]
    annotations: Optional[List[Annotation]]
    links: Optional[List[Link]]
    remarks: Optional[MarkupMultiLine]

    class Config:
        fields = {"short_name": "short-name"}
        allow_population_by_field_name = True


class ResponsibleParty(OSCALElement):
    class Config:
        fields = {"role_id": "role-id", "party_uuids": "party-uuids"}
        allow_population_by_field_name = True

    role_id: str
    party_uuids: List[UUID]
    props: Optional[List[Property]]
    links: Optional[List[Link]]
    remarks: Optional[MarkupMultiLine]


class Metadata(OSCALElement):
    class Config:
        fields = {
            "oscal_version": "oscal-version",
            "document_ids": "document-ids",
            "last_modified": "last-modified",
            "responsible_parties": "responsible-parties",
        }
        exclude_if_false = ["responsible-parties"]
        allow_population_by_field_name = True

    title: str
    published: datetime = datetime.now(timezone.utc)
    last_modified: datetime = datetime.now(timezone.utc)
    version: str
    oscal_version: str = OSCAL_VERSION
    revisions: Optional[List[Revision]]
    document_ids: Optional[List[DocumentId]]
    props: Optional[List[Property]]
    links: Optional[List[Link]]
    roles: Optional[List[Role]]
    locations: Optional[List[Location]]
    parties: Optional[List[Party]]
    responsible_parties: Optional[List[ResponsibleParty]]
    remarks: Optional[MarkupMultiLine]


class Parameter(OSCALElement):
    class Config:
        fields = {"param_class": "class", "depends_on": "depends-on"}
        allow_population_by_field_name = True

    id: NCName
    param_class: Optional[str]
    depends_on: Optional[str]
    links: Optional[List[Link]]
    label: Optional[MarkupLine]
    usage: Optional[MarkupMultiLine]
    constraints: Optional[List[Constraint]]
    guidelines: Optional[List[Guideline]]
    values: List[str] = []
    select: Optional[Select]
    remarks: Optional[MarkupMultiLine]

    @property
    def get_odp_text(self):
        if guidelines := getattr(self, "guidelines"):
            gl = []
            [gl.append(g.prose) for g in guidelines]
            text = " ".join(gl)
        elif select := getattr(self, "select"):
            text = select.get_select_text
        elif values := getattr(self, "values"):
            vl = []
            [vl.append(v) for v in values]
            text = " ".join(vl)
        else:
            text = self.label

        return text


class ResponsibleRole(OSCALElement):
    class Config:
        fields = {"role_id": "role-id", "party_uuids": "party-uuids"}
        allow_population_by_field_name = True

    role_id: RoleIDEnum
    props: Optional[List[Property]]
    links: Optional[List[Link]]
    party_uuids: Optional[List[UUID]]
    remarks: Optional[MarkupMultiLine]
