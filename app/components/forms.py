from flask_wtf import FlaskForm
from wtforms import FileField, HiddenField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, length, optional

from app.oscal.component import ComponentTypeEnum
from app.oscal.validator import OscalValidator


def validate_component_file(form, field) -> OscalValidator:
    validate = OscalValidator(field.data, "oscal_catalog_schema.json")
    field.data.seek(0)
    return validate


class ComponentForm(FlaskForm):
    title = StringField(
        "Component Name",
        validators=[InputRequired()],
    )
    description = TextAreaField(
        "Description",
        validators=[optional(), length(max=200)],
        render_kw={
            "placeholder": "Enter a short description, 200 characters or less",
        },
    )
    component_type = SelectField(
        "Component Type",
        choices=[(v.name, v.value) for v in ComponentTypeEnum],
        default=ComponentTypeEnum.software.value,
    )
    component_file = FileField(
        "Upload File",
        validators=[validate_component_file],
        render_kw={
            "type": "file",
        },
    )


class UpdateComponentForm(FlaskForm):
    name = StringField(
        "Catalog Name",
        validators=[InputRequired()],
    )
    description = TextAreaField(
        "Description",
        validators=[optional(), length(max=200)],
        render_kw={
            "placeholder": "Enter a short description, 200 characters or less",
        },
    )


class ComponentAddForm(FlaskForm):
    component_id = HiddenField(
        validators=[InputRequired()],
        render_kw={"id": "add-component"},
    )
