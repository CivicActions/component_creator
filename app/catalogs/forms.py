from flask_wtf import FlaskForm
from wtforms import FileField, StringField, TextAreaField
from wtforms.validators import InputRequired, length, optional

from app.oscal.validator import OscalValidator


def validate_catalog_file(form, field) -> bool:
    validate = OscalValidator(field.data, "oscal_catalog_schema.json")
    field.data.seek(0)
    return validate


class CatalogForm(FlaskForm):
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
        validators=[optional(), length(max=200)],
        render_kw={
            "class": "textarea",
            "placeholder": "Enter a short description, 200 characters or less",
        },
    )
    catalog_file = FileField(
        "Upload File",
        validators=[InputRequired(), validate_catalog_file],
        render_kw={
            "class": "file-input",
            "type": "file",
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
        validators=[optional(), length(max=200)],
        render_kw={
            "class": "textarea",
            "placeholder": "Enter a short description, 200 characters or less",
        },
    )
