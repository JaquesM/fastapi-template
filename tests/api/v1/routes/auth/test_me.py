from fastapi.testclient import TestClient

from app.models.user import UserRole, SuperUserRole
from app.schemas.auth import MyUserResponse

ME_PATH = "/v1/auth/me"

# Unit tests
def test_me_endpoint(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.get(ME_PATH)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(MyUserResponse.model_fields.keys()).issubset(content.keys())
    assert content["is_superuser"] == False
    assert len(content["customers"]) > 0
    assert content["customers"][0]["role"] == UserRole.MANAGER


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.get(ME_PATH)
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_authenticated_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.get(ME_PATH)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(MyUserResponse.model_fields.keys()).issubset(content.keys())
    assert content["is_superuser"] == False
    assert len(content["customers"]) > 0
    assert content["customers"][0]["role"] == UserRole.VISITOR

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.get(ME_PATH)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(MyUserResponse.model_fields.keys()).issubset(content.keys())
    assert content["is_superuser"] == True
    assert len(content["customers"]) == 0
