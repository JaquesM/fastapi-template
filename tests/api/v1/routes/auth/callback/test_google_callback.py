from app.models.user import UserRole
from app.schemas.auth import CallbackAuthInput

CALLBACK_GOOGLE_PATH = "/v1/auth/callback/google"

# Unit tests
def test_google_callback_missing_info(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    response = client.post(CALLBACK_GOOGLE_PATH)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_google_callback_no_valid_customer(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_callback_google_input()
    body["customer_subdomain"] = "invalid_customer"
    response = client.post(CALLBACK_GOOGLE_PATH, json=body)
    content = response.json()
    assert response.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "Customer not found."

def test_google_callback_invalid_token(auth_client) -> None:
    client = auth_client(UserRole.MANAGER)
    body = create_callback_google_input()
    body["token"] = "invalid_token"
    response = client.post(CALLBACK_GOOGLE_PATH, json=body)
    content = response.json()
    assert response.status_code == 400
    assert content["detail"] == "An error occurred with Google OAuth."


# Helper functions
def create_callback_google_input() -> CallbackAuthInput:
    return CallbackAuthInput(
        token="test_token",
        customer_subdomain="test-customer-0",
        callback_url="http://localhost:3000",
    ).model_dump(mode="json")

