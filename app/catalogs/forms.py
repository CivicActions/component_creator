from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField
from wtforms.validators import InputRequired, length

from app.oscal.validator import OscalValidator


def validate_catalog_file(form, field) -> OscalValidator:
    validate = OscalValidator(field.data, "oscal_catalog_schema.json")
    field.data.seek(0)
    return validate


class CatalogForm(FlaskForm):
    title = StringField(
        "Catalog Name",
        validators=[InputRequired()],
        render_kw={
            "type": "text",
            "required": "required",
        },
    )
    description = TextAreaField(
        "Description",
        validators=[length(max=200)],
        render_kw={
            "required": "required",
            "placeholder": "Enter a short description, 200 characters or less",
        },
    )
    source = StringField(
        "Source",
        validators=[length(max=150)],
        render_kw={
            "required": "required",
            "placeholder": "Enter the source URL for this catalog.",
        },
    )
    catalog_file = FileField(
        "Upload File",
        validators=[InputRequired(), validate_catalog_file],
        render_kw={
            "type": "file",
            "required": "required",
        },
    )


class UpdateCatalogForm(FlaskForm):
    title = StringField(
        "Catalog Name",
        validators=[InputRequired()],
        render_kw={
            "class": "input",
            "type": "text",
        },
    )
    description = TextAreaField(
        "Description",
        validators=[InputRequired(), length(max=200)],
        render_kw={
            "class": "textarea",
            "placeholder": "Enter a short description, 200 characters or less",
        },
    )
    source = StringField(
        "Source",
        validators=[InputRequired(), length(max=150)],
        render_kw={
            "placeholder": "Enter the source URL for this catalog.",
        },
    )
