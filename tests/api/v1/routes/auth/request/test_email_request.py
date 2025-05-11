import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.models.user import UserRole, SuperUserRole
from app.schemas.auth import RequestAuthInput, RedirectURLResponse
from app.crud.user.user_session import retrieve_user_sessions_by_user_id
from app.crud.user import get_user_by_email
from app.services.boto3 import get_aws_session

REQUEST_EMAIL_PATH = "/v1/auth/request/email"

# Unit tests
def test_email_request_missing_info(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(REQUEST_EMAIL_PATH)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_email_request_no_valid_user(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_email_input()
    body["email"] = "invalid_email"
    response = client.post(REQUEST_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "A user with this email does not exist in the system."

def test_email_request_no_valid_customer(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_email_input()
    body["customer_subdomain"] = "invalid_customer"
    response = client.post(REQUEST_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "Customer not found."

def test_email_request_no_access_to_customer(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_email_input()
    body["customer_subdomain"] = "test-customer-1"
    response = client.post(REQUEST_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 403
    assert isinstance(content, dict)
    assert content["detail"] == "The user has no access to this customer."

def test_email_request(auth_client, patch_email_if_unavailable) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(REQUEST_EMAIL_PATH, json=create_request_email_input())
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(RedirectURLResponse.model_fields.keys()).issubset(content.keys())
    assert content["redirect_url"] == "Magic link email sent"

def test_email_request_home(auth_client, patch_email_if_unavailable) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_email_input()
    body["customer_subdomain"] = "home"
    response = client.post(REQUEST_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(RedirectURLResponse.model_fields.keys()).issubset(content.keys())
    assert content["redirect_url"] == "Magic link email sent"

def test_email_request_admin(auth_client, patch_email_if_unavailable) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_email_input()
    body["customer_subdomain"] = "admin"
    response = client.post(REQUEST_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 403
    assert isinstance(content, dict)
    assert content["detail"] == "This user doesn't have enough privileges."


# Integration tests
def test_email_request_integration(auth_client, db, patch_email_if_unavailable) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_request_email_input()
    _response = client.post(REQUEST_EMAIL_PATH, json=body)
    user = get_user_by_email(session=db, email=body["email"])
    user_sessions = retrieve_user_sessions_by_user_id(session=db, user_id=user.id)
    assert len(user_sessions) >= 1
    assert user_sessions[-1].magic_link_token is not None
    assert user_sessions[-1].magic_link_requested_at is not None
    assert user_sessions[-1].magic_link_used_at is None
    assert user_sessions[-1].magic_link_expires_at is not None
    assert user_sessions[-1].refresh_token is not None


# Authorization tests
def test_non_authenticated_user(client, patch_email_if_unavailable) -> None:
    client = TestClient(client.app)
    response = client.post(REQUEST_EMAIL_PATH, json=create_request_email_input())
    assert response.status_code == 200

def test_authenticated_user(auth_client, patch_email_if_unavailable) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post(REQUEST_EMAIL_PATH, json=create_request_email_input())
    assert response.status_code == 200

def test_superuser(superuser_client, patch_email_if_unavailable) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.post(REQUEST_EMAIL_PATH, json=create_request_email_input())
    assert response.status_code == 200


# Helper functions
def create_request_email_input() -> RequestAuthInput:
    return RequestAuthInput(
        email="test_user_0@email.com",
        customer_subdomain="test-customer-0",
        callback_url="https://example.com/?link="
    ).model_dump(mode="json")


# Email server
@pytest.fixture(scope="session", autouse=False)
def patch_email_if_unavailable():
    if len(get_aws_session().available_profiles) == 0:
        with patch("app.core.security.providers.email.send_email", return_value=None) as mock_send:
            yield mock_send
    else:
        yield None


