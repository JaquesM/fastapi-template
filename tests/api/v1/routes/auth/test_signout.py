from fastapi.testclient import TestClient

from app.models.user import UserRole, SuperUserRole
from app.schemas import Message

SIGNOUT_PATH = "/v1/auth/signout"

# Unit tests
def test_signout(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(SIGNOUT_PATH)
    content = response.json()
    response2 = client.get("/v1/auth/me")
    content2 = response2.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(Message.model_fields.keys()).issubset(content.keys())
    assert content["message"] == "User signed out successfully."
    assert response2.status_code == 401
    assert content2["detail"] == "The user is not authenticated."


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.post(SIGNOUT_PATH)
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_authenticated_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.post(SIGNOUT_PATH)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(Message.model_fields.keys()).issubset(content.keys())

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.post(SIGNOUT_PATH)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(Message.model_fields.keys()).issubset(content.keys())
