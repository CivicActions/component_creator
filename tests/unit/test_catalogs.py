from app.catalogs.routes import allowed_file, get_control_links, replace_odps
from app.oscal.catalog import CatalogModel


def test_new_catalog(catalog):
    """
    GIVEN a Catalog model
    WHEN a new Catalog is created
    THEN check the title, description, and filename
    """
    assert catalog.title == "Test Catalog"
    assert catalog.description == "This is the description"
    assert catalog.filename == "tests/data/NIST_SP_800-53_rev5_TEST.json"


def test_allowed_file():
    """
    allowed_file only allows json filenames
    """
    json_file = allowed_file("TEST_Catalog.json")
    txt_file = allowed_file("TEST_Catalog.txt")
    csv_file = allowed_file("TEST_Catalog.csv")
    assert json_file is True
    assert txt_file is False
    assert csv_file is False


def test_get_control_links(catalog):
    catalog = CatalogModel.from_json(catalog.filename)
    backmatter = catalog.back_matter
    control = catalog.get_control("ac-2")
    links = get_control_links(
        links=control.links,
        backmatter=backmatter,
    )
    references = links.get("reference")
    related = links.get("related")
    assert type(links) == dict
    assert type(references) == list
    assert type(related) == list
    assert len(references) == 3
    assert len(related) == 28


def test_odp_replacement():
    """
    replace_odps should replace parameters in string.
    """
    to_replace = [
        {"prose": "{{ insert: param, first }} was the first man on the moon."},
        {"prose": "{{ insert: param, second }} was the first Life on Mars."},
        {
            "prose": "{{ insert: param, first }} was shorter than {{ insert: param, second }}."
        },
    ]
    replace_with = {
        "first": "Neil Armstrong",
        "second": "David Bowie",
    }
    replaced = replace_odps(to_replace, replace_with)
    assert replaced[0].get("prose") == "Neil Armstrong was the first man on the moon."
    assert replaced[1].get("prose") == "David Bowie was the first Life on Mars."
    assert replaced[2].get("prose") == "Neil Armstrong was shorter than David Bowie."
