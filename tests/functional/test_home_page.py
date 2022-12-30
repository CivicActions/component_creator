def test_home_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Component Creator" in response.data
