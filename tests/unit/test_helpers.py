from app.helpers import allowed_file


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
