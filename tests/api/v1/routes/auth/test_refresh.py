from fastapi.testclient import TestClient
from sqlmodel import select

from app.models import UserSession
from app.schemas.auth import RefreshTokenResponse

REFRESH_PATH = "/v1/auth/refresh"

# Unit tests
def test_refresh_endpoint_invalid_token(client) -> None:
    client = TestClient(client.app)
    response = client.post(REFRESH_PATH, headers={"Authorization": f"Bearer {'invalid_token'}"})
    content = response.json()
    assert response.status_code == 400
    assert isinstance(content, dict)
    assert content["detail"] == "Invalid refresh token."

def test_refresh_endpoint_revoked(client, db) -> None:
    user_session = db.exec(
        select(UserSession)
        .where(UserSession.is_revoked == True)
        .where(UserSession.refresh_token.is_not(None))
    ).first()
    client = TestClient(client.app)
    response = client.post(REFRESH_PATH, headers={"Authorization": f"Bearer {user_session.refresh_token}"})
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "Token has been revoked."

def test_refresh_endpoint(client, db) -> None:
    user_session = db.exec(
        select(UserSession)
        .where(UserSession.is_revoked == False)
        .where(UserSession.refresh_token.is_not(None))
    ).first()
    client = TestClient(client.app)
    response = client.post(REFRESH_PATH, headers={"Authorization": f"Bearer {user_session.refresh_token}"})
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert set(RefreshTokenResponse.model_fields.keys()).issubset(content.keys())
    assert len(content["access_token"]) > 4


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.post(REFRESH_PATH)
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

