import enum

from app.extensions import Base, db

catalogs = db.Table(
    "catalogs",
    db.Column("catalog_id", db.Integer, db.ForeignKey("catalog.id"), primary_key=True),
    db.Column(
        "component_id", db.Integer, db.ForeignKey("component.id"), primary_key=True
    ),
)


class TypesEnum(enum.Enum):
    INTERCONNECT = "interconnection", "Interconnection"
    SOFTWARE = "software", "Software"
    HARDWARE = "hardware", "Hardware"
    SERVICE = "service", "Service"
    POLICY = "policy", "Policy"
    PHYSICAL = "physical", "Physical"
    PROCESS = "process-procedure", "Process/Procedure"
    PLAN = "plan", "Plan"
    GUIDANCE = "guidance", "Guidance"
    STANDARD = "standard", "Standard"
    VALIDATION = "validation", "Validation"


class Catalog(Base):
    __tablename__ = "catalog"

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<Catalog '{self.title}'"


class Component(Base):
    __tablename__ = "component"

    title = db.Column(db.String(150), nullable=False)
    type = db.Column(
        db.Enum(TypesEnum),
        nullable=False,
        default=TypesEnum.SOFTWARE.value,
    )
    filename = db.Column(db.String(150), nullable=False)
    catalog = db.relationship(
        "Catalog",
        secondary=catalogs,
        lazy="subquery",
        backref=db.backref("components", lazy=True),
    )

    def __repr__(self):
        return f"<Component '{self.title}'"
