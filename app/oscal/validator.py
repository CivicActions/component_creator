import json
from dataclasses import dataclass, field
from io import BufferedReader
from pathlib import Path

import jsonschema
import jsonschema.exceptions as exceptions
from flask import current_app


@dataclass
class OscalValidator:
    file: BufferedReader
    validator: str
    oscal_schema: dict = field(default_factory=dict)

    def validate_file(self) -> bool:
        try:
            json_file = json.load(self.file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Unable to load file: {self.file}")

        self.get_validator()
        try:
            jsonschema.validate(instance=json_file, schema=self.oscal_schema)
        except exceptions.ValidationError as exc:
            raise exceptions.ValidationError(
                f"{json_file} is not a valid OSCAL."
            ) from exc
        except exceptions.SchemaError as exc:
            raise exceptions.ValidationError(
                f"{self.oscal_schema} schema is not a valid OSCAL schema."
            ) from exc
        return True

    def get_validator(self):
        schema = Path(current_app.config["BASEPATH"]).joinpath(
            "oscal", "schemas", self.validator
        )
        with open(schema, "r") as f:
            self.oscal_schema = json.load(f)
