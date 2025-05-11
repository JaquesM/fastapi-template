from sqlmodel import select
from fastapi.testclient import TestClient

from app.models import UserSession
from app.models.user import UserRole
from app.schemas.auth import CallbackAuthInput, AccessRefreshTokenResponse
from app.crud.user.user_session import retrieve_user_session_by_magic_link_token

CALLBACK_EMAIL_PATH = "/v1/auth/callback/email"

# Unit tests
def test_email_callback_missing_info(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(CALLBACK_EMAIL_PATH)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_email_callback_no_valid_customer(auth_client, db) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_callback_email_input(db)
    body["customer_subdomain"] = "invalid_customer"
    response = client.post(CALLBACK_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "Customer not found."

def test_email_callback_invalid_token(auth_client, db) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_callback_email_input(db)
    body["token"] = "invalid_token"
    response = client.post(CALLBACK_EMAIL_PATH, json=body)
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "Invalid token."

def test_email_callback(auth_client, db) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(CALLBACK_EMAIL_PATH, json=create_callback_email_input(db))
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(AccessRefreshTokenResponse.model_fields.keys()).issubset(content.keys())
    assert len(content["access_token"]) > 4
    assert len(content["refresh_token"]) > 4


# Integration tests
def test_email_callback_integration(auth_client, db) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_callback_email_input(db)
    _response = client.post(CALLBACK_EMAIL_PATH, json=body)
    user_session = retrieve_user_session_by_magic_link_token(session=db, magic_link_token=body["token"])
    assert user_session.magic_link_token is not None
    assert user_session.magic_link_used_at is not None
    assert user_session.magic_link_expires_at is not None
    assert user_session.refresh_token is not None
    assert user_session.last_used is not None


# Authorization tests
def test_non_authenticated_user(client, db) -> None:
    client = TestClient(client.app)
    response = client.post(CALLBACK_EMAIL_PATH, json=create_callback_email_input(db))
    assert response.status_code == 200

def test_authenticated_user(auth_client, db) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post(CALLBACK_EMAIL_PATH, json=create_callback_email_input(db))
    assert response.status_code == 200


# Helper functions
def create_callback_email_input(session) -> CallbackAuthInput:
    user_session = session.exec(
        select(UserSession)
        .where(UserSession.magic_link_used_at == None)
        .where(UserSession.magic_link_token != None)
    ).first()

    return CallbackAuthInput(
        token=user_session.magic_link_token if user_session else "test_token",
        customer_subdomain="test-customer-0",
        callback_url=None,
    ).model_dump(mode="json")

