import pytest

from app import create_app
from app.extensions import db
from app.models.components import CatalogFile, ComponentFile
from config import TestConfig


@pytest.fixture(scope="module")
def catalog():
    catalog = CatalogFile(
        title="Test Catalog",
        description="This is the description",
        source="https://pages.nist.gov/OSCAL/",
        filename="tests/data/NIST_SP_800-53_rev5_TEST.json",
    )
    return catalog


@pytest.fixture(scope="module")
def component():
    component = ComponentFile(
        title="Testing Component",
        description="This is the description",
        type="software",
    )
    return component


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app(config_class=TestConfig)

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope="module")
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert data
    db.session.add_all(
        [
            CatalogFile(
                title="Test Catalog",
                description="This is the description",
                source="https://pages.nist.gov/OSCAL/",
                filename="tests/data/NIST_SP_800-53_rev5_TEST.json",
            ),
            CatalogFile(
                title="Test Catalog Too",
                description="This is another description",
                source="https://pages.nist.gov/OSCAL/2",
                filename="tests/data/NIST_SP_800-53_rev5_TEST.json",
            ),
            ComponentFile(
                title="Test Component One",
                description="A Component for testing.",
                type="software",
                filename="tests/data/component_one.json",
            ),
            ComponentFile(
                title="Test Component Two",
                description="A Component for testing as well.",
                type="software",
                filename="tests/data/component_two.json",
            ),
        ]
    )

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()
