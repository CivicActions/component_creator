def test_catalog_list(test_client, init_database):
    """
    GIVEN a Flask application
    WHEN the '/catalogs' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/catalogs/")
    assert response.status_code == 200
    assert b"Test Catalog" in response.data
    assert b"Test Catalog Too" in response.data
    assert b"This is the description" in response.data
    assert b"This is another description" in response.data


def test_catalog_add(test_client, init_database):
    """
    GIVEN a Flask application
    WHEN the '/catalogs/add' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/catalogs/create")
    assert response.status_code == 200
    assert b"Add a Catalog" in response.data


def test_catalog_view(test_client, init_database):
    """
    GIVEN a Flask application
    WHEN the '/catalogs/1' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/catalogs/1")
    assert response.status_code == 200
    assert b"NIST Special Publication 800-53 Revision 5 TEST" in response.data
    assert b"AC: Access Control" in response.data
    assert b"Policy and Procedures" in response.data
    assert b"SR: Supply Chain Risk Management" in response.data
    assert b"Supply Chain Risk Management Plan" in response.data
    assert b"Establish SCRM Team" in response.data


def test_catalog_update_page(test_client, init_database):
    """
    GIVEN a Flask application
    WHEN the '/catalogs/1/update' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/catalogs/1/update")
    assert response.status_code == 200
    assert b"Update Catalog" in response.data
    assert b"Test Catalog" in response.data
    assert b"This is the description" in response.data
