
from app.core.config import settings


# Unit tests
def test_contact_incomplete(client) -> None:
    response = client.post("/v1/contact", json={
        "name": None,
        "email": settings.EMAIL_TEST_USER,
        "phone": "Test",
        "company": "Test"
    })
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Input should be a valid string"

def test_contact(client) -> None:
    response = client.post("/v1/contact", json={
        "name": "Test",
        "email": settings.EMAIL_TEST_USER,
        "phone": "Test",
        "company": "Test"
    })
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert content["message"] == "Contact info sent successfully"


# Integration tests
def test_contact_email_sent(client) -> None:
    pass

