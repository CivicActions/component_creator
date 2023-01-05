from app.components.routes import add_implemented_requirement
from app.oscal.component import ImplementedRequirement


def test_add_implemented_requirements():
    """
    Given a Control ID
    add_implemented_requirement should return an object of the type ImplementedRequirement
    """
    ir = add_implemented_requirement("ac-1")
    assert type(ir) == ImplementedRequirement
    assert ir.description == "Add Control narrative"
    assert ir.control_id == "ac-1"
    assert hasattr(ir, "props")
    assert hasattr(ir, "set_parameters")
