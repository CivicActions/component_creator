import pytest

from app import create_app
from app.extensions import db
from app.models.components import Catalog
from config import TestConfig


@pytest.fixture(scope="module")
def catalog():
    catalog = Catalog(
        title="Test Catalog",
        description="This is the description",
        filename="tests/data/NIST_SP_800-53_rev5_TEST.json",
    )
    return catalog


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

    # Insert user data
    catalog1 = Catalog(
        title="Test Catalog",
        description="This is the description",
        filename="tests/data/NIST_SP_800-53_rev5_TEST.json",
    )
    catalog2 = Catalog(
        title="Test Catalog Too",
        description="This is another description",
        filename="tests/data/NIST_SP_800-53_rev5_TEST.json",
    )
    db.session.add(catalog1)
    db.session.add(catalog2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()
