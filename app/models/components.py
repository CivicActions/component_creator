from flask import current_app, flash

from app.extensions import Base, db
from app.oscal.component import ComponentModel, ComponentTypeEnum

component_catalog = db.Table(
    "component_catalog",
    db.Column(
        "component_id", db.Integer, db.ForeignKey("components.id"), primary_key=True
    ),
    db.Column("catalog_id", db.Integer, db.ForeignKey("catalogs.id"), primary_key=True),
)


class CatalogFile(Base):
    __tablename__ = "catalogs"

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return self.title


class ComponentFile(Base):
    __tablename__ = "components"

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(
        db.Enum(ComponentTypeEnum),
        nullable=False,
        default=ComponentTypeEnum.software.name,
    )
    filename = db.Column(db.String(150), nullable=False)
    catalogs = db.relationship(
        "CatalogFile",
        secondary=component_catalog,
        backref="components",
    )

    def __repr__(self):
        return self.title

    def write_file(self, component: ComponentModel):
        json_file = component.json(indent=2)
        try:
            with open(self.filename, "w+") as f:
                f.write(json_file)
        except IOError as exc:
            flash("Error writing Component file.", "error")
            current_app.logger(f"Error writing file {self.filename}: {exc}")
