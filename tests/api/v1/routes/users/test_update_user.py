import random
from datetime import datetime

from app.models.user import UserRole, SuperUserRole
from app.schemas.users import UserResponse, UpdateUser
from app.crud.user import retrieve_users_by_customer_id
from app.crud.campaign import retrieve_customer_campaigns
from app.crud.customer import get_customer_by_subdomain

from fastapi.testclient import TestClient


UPDATE_USER_PATH = "/v1/users/test-customer-0/00000000-0000-0000-0000-000000000000"

# Unit tests
def test_update_user_incomplete(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_USER_PATH, json={
        "name": "Test Create User 0",
        "email": "test-create-user-0@email.com",
    })
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_update_user_non_existent(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_USER_PATH[:-3] + "999", json=update_user_input())
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "User not found."

def test_update_user_no_customer_link(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_USER_PATH[:-1] + "1", json=update_user_input())
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "This user has no access to this customer."

def test_update_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_USER_PATH, json=update_user_input())
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert UserResponse(**content)

def test_update_visitor_user(db, auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    campaigns = retrieve_customer_campaigns(session=db, customer_id=customer.id)
    user_input = update_user_input(role=UserRole.VISITOR)
    response_1 = manager_client.put(UPDATE_USER_PATH, json=user_input)
    content_1 = response_1.json()
    user_input["campaign_ids"] = ["00000000-0000-0000-0000-000000000000"]
    response_2 = manager_client.put(UPDATE_USER_PATH, json=user_input)
    content_2 = response_2.json()
    user_input["campaign_ids"] = [str(campaigns[0].id)]
    response_3 = manager_client.put(UPDATE_USER_PATH, json=user_input)
    assert response_1.status_code == 422
    assert isinstance(content_1, dict)
    assert content_1["detail"] == "Invalid user role requirements."
    assert response_2.status_code == 404
    assert content_2["detail"] == "Campaign not associated with the customer."
    assert response_3.status_code == 200


# Integration tests
def test_update_user_db(db, auth_client) -> None:
    user_id = UPDATE_USER_PATH.split("/")[-1]
    date_before = datetime.now()
    manager_client = auth_client(UserRole.MANAGER)
    user_input = update_user_input(UserRole.ANALYST)
    manager_client.put(UPDATE_USER_PATH, json=user_input)
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    users = retrieve_users_by_customer_id(session=db, customer_id=customer.id)
    user = next((user for user in users if str(user.id) == user_id), None)
    assert user
    assert user.role == user_input["role"]
    assert user.updated_at > date_before


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.put(UPDATE_USER_PATH, json=update_user_input())
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_USER_PATH.replace("test-customer-0", "test-customer-1"), json=update_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_USER_PATH.replace("test-customer-0", "test-customer-404"), json=update_user_input())
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.put(UPDATE_USER_PATH, json=update_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.put(UPDATE_USER_PATH, json=update_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.put(UPDATE_USER_PATH, json=update_user_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.put(UPDATE_USER_PATH, json=update_user_input())
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


# Helper functions
def update_user_input(
        role=random.choice([UserRole.MANAGER, UserRole.ANALYST, UserRole.OPERATION]),
        campaign_ids=[],
) -> UpdateUser:
    return UpdateUser(
        role=role,
        campaign_ids=campaign_ids,
    ).model_dump(mode="json")

