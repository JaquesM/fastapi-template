import random

from app.models.user import UserRole, SuperUserRole
from app.schemas.users import UserResponse, CreateUser
from app.crud.user import retrieve_users_by_customer_id
from app.crud.campaign import retrieve_customer_campaigns
from app.crud.customer import get_customer_by_subdomain

from fastapi.testclient import TestClient

# Unit tests
def test_create_incomplete_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post("/v1/users/test-customer-0", json={
        "name": "Test Create User 0",
        "email": "test-create-user-0@email.com",
    })
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_create_user_same_email(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    user_input_1 = create_user_input()
    user_input_1["email"] = "test_create_user_same_email@test.com"
    user_input_2 = create_user_input()
    user_input_2["email"] = "test_create_user_same_email@test.com"
    response_1 = manager_client.post("/v1/users/test-customer-0", json=user_input_1)
    response_2 = manager_client.post("/v1/users/test-customer-0", json=user_input_2)
    content = response_2.json()
    assert response_1.status_code == 200
    assert response_2.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "A user with this email already exists for that customer."

def test_create_user_complex_name(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    user_input = create_user_input()
    user_input["name"] = "Usuário número 1ç"
    response = manager_client.post("/v1/users/test-customer-0", json=user_input)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"] == "Invalid user name."

def test_create_user_invalid_email(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    user_input = create_user_input()
    user_input["email"] = "email@invalid"
    response = manager_client.post("/v1/users/test-customer-0", json=user_input)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"] == "Invalid user email."

def test_create_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    user_input = create_user_input()
    response = manager_client.post("/v1/users/test-customer-0", json=user_input)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert UserResponse(**content)

def test_create_visitor_user(db, auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    campaigns = retrieve_customer_campaigns(session=db, customer_id=customer.id)
    user_input = create_user_input()
    user_input["role"] = UserRole.VISITOR
    response_1 = manager_client.post("/v1/users/test-customer-0", json=user_input)
    content_1 = response_1.json()
    user_input["campaign_ids"] = ["00000000-0000-0000-0000-000000000000"]
    response_2 = manager_client.post("/v1/users/test-customer-0", json=user_input)
    content_2 = response_2.json()
    user_input["campaign_ids"] = [str(campaigns[0].id)]
    response_3 = manager_client.post("/v1/users/test-customer-0", json=user_input)
    assert response_1.status_code == 422
    assert isinstance(content_1, dict)
    assert content_1["detail"] == "Invalid user role requirements."
    assert response_2.status_code == 404
    assert content_2["detail"] == "Campaign not associated with the customer."
    assert response_3.status_code == 200


# Integration tests
def test_create_user_db(db, auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    user_input = create_user_input()
    manager_client.post("/v1/users/test-customer-0", json=user_input)
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    users = retrieve_users_by_customer_id(session=db, customer_id=customer.id)
    user = next((user for user in users if user.name == user_input["name"]), None)
    assert user
    assert user.name == user_input["name"]
    assert user.email == user_input["email"]
    assert user.role == user_input["role"]
    assert user.status == "active"


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.post("/v1/users/test-customer-0", json=create_user_input())
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post("/v1/users/test-customer-1", json=create_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post("/v1/users/test-customer-404", json=create_user_input())
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.post("/v1/users/test-customer-0", json=create_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.post("/v1/users/test-customer-0", json=create_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.post("/v1/users/test-customer-0", json=create_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.post("/v1/users/test-customer-0", json=create_user_input())
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


# Helper functions
def create_user_input() -> CreateUser:
    return CreateUser(
        name=f"Test Create User {random.randint(0, 1000)}",
        email=f"test_create_user_{random.randint(0, 1000)}@example.com",
        phone="111-222-3333",
        role=random.choice([UserRole.MANAGER, UserRole.ANALYST, UserRole.OPERATION]),
        campaign_ids=[],
    ).model_dump(mode="json")

