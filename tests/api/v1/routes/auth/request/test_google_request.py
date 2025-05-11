from fastapi.testclient import TestClient

from app.models.user import UserRole, SuperUserRole
from app.schemas.auth import RequestAuthInput, RedirectURLResponse

REQUEST_GOOGLE_PATH = "/v1/auth/request/google"

# Unit tests
def test_google_request_missing_info(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(REQUEST_GOOGLE_PATH)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_google_request_no_valid_customer(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_google_input()
    body["customer_subdomain"] = "invalid_customer"
    response = client.post(REQUEST_GOOGLE_PATH, json=body)
    content = response.json()
    assert response.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "Customer not found."

def test_google_request(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(REQUEST_GOOGLE_PATH, json=create_request_google_input())
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(RedirectURLResponse.model_fields.keys()).issubset(content.keys())
    assert content["redirect_url"].split("?")[0] == "https://accounts.google.com/o/oauth2/auth"

def test_google_request_home_and_admin(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_google_input()
    body["customer_subdomain"] = "home"
    response1 = client.post(REQUEST_GOOGLE_PATH, json=body)
    body["customer_subdomain"] = "admin"
    response2 = client.post(REQUEST_GOOGLE_PATH, json=body)
    assert response1.status_code == 200
    assert response2.status_code == 200


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.post(REQUEST_GOOGLE_PATH, json=create_request_google_input())
    assert response.status_code == 200

def test_authenticated_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post(REQUEST_GOOGLE_PATH, json=create_request_google_input())
    assert response.status_code == 200

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.post(REQUEST_GOOGLE_PATH, json=create_request_google_input())
    assert response.status_code == 200


# Helper functions
def create_request_google_input() -> RequestAuthInput:
    return RequestAuthInput(
        email=None,
        customer_subdomain="test-customer-0",
        callback_url=None
    ).model_dump(mode="json")

