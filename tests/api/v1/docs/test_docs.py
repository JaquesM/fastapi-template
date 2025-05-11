

def test_stoplight_docs_endpoint_active(client) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Stoplight" in response.text

def test_swagger_docs_endpoint_active(client) -> None:
    response = client.get("/swagger")
    assert response.status_code == 200
    assert "Swagger UI" in response.text

def test_redoc_docs_endpoint_active(client) -> None:
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "redoc" in response.text


