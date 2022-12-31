import enum

from app.extensions import Base, db

catalogs = db.Table(
    "catalogs",
    db.Column("catalog_id", db.Integer, db.ForeignKey("catalog.id"), primary_key=True),
    db.Column(
        "component_id", db.Integer, db.ForeignKey("component.id"), primary_key=True
    ),
)


class ComponentTypes(enum.Enum):
    SOFTWARE = ("software", "Software")
    GUIDANCE = ("guidance", "Guidance")
    HARDWARE = ("hardware", "Hardware")
    INTERCONNECT = ("interconnection", "Interconnection")
    PHYSICAL = ("physical", "Physical")
    PLAN = ("plan", "Plan")
    POLICY = ("policy", "Policy")
    PROCESS = ("process-procedure", "Process/Procedure")
    SERVICE = ("service", "Service")
    STANDARD = ("standard", "Standard")
    VALIDATION = ("validation", "Validation")


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
    description = db.Column(db.Text, nullable=False)
    type = db.Column(
        db.Enum(ComponentTypes),
        nullable=False,
        default=ComponentTypes.SOFTWARE.value,
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
