from fastapi.testclient import TestClient

from app.models.user import UserRole, SuperUserRole
from app.schemas.users import UserResponse

# Unit tests
def test_list_users(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.get("/v1/users/test-customer-0")
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, list)
    assert len(content) >= 2
    for item in content:
        assert isinstance(item, dict)
        assert set(UserResponse.model_fields.keys()).issubset(item.keys())


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.get("/v1/users/test-customer-0")
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.get("/v1/users/test-customer-1")
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.get("/v1/users/test-customer-404")
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.get("/v1/users/test-customer-0")
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.get("/v1/users/test-customer-0")
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.get("/v1/users/test-customer-0")
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.get("/v1/users/test-customer-0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
