from sqlmodel import select
from fastapi.testclient import TestClient

from app.models.user import UserRole, SuperUserRole
from app.models.campaign import Campaign

DELETE_CAMPAIGN_PATH = lambda id: f"/v1/campaigns/test-customer-0/00000000-0000-0000-0000-000000000{str(id).zfill(3)}"

# Unit tests
def test_delete_campaign(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.delete(DELETE_CAMPAIGN_PATH(101))
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, object)
    assert content["message"] == "Campaign deleted successfully."


# Integration tests
def test_delete_campaign_db(db) -> None:
    campaign = db.exec(select(Campaign).where(Campaign.name == "Test Campaign 101")).first()
    assert campaign is None


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.delete(DELETE_CAMPAIGN_PATH(102))
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.delete(DELETE_CAMPAIGN_PATH(102).replace("test-customer-0", "test-customer-1"))
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.delete(DELETE_CAMPAIGN_PATH(102).replace("test-customer-0", "test-customer-404"))
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_campaign_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.delete(DELETE_CAMPAIGN_PATH(101))
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Campaign not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.delete(DELETE_CAMPAIGN_PATH(103))
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.delete(DELETE_CAMPAIGN_PATH(104))
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.delete(DELETE_CAMPAIGN_PATH(104))
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.delete(DELETE_CAMPAIGN_PATH(104))
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, object)
    assert content["message"] == "Campaign deleted successfully."
