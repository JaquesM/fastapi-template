from app.models.user import UserRole, SuperUserRole
from app.schemas.campaigns import CampaignResponse
from app.schemas.users import UpdateUser
from app.crud.campaign import retrieve_customer_campaigns
from app.crud.customer import get_customer_by_subdomain
from app.crud.user import update_user_customer_link, get_user_by_email

from fastapi.testclient import TestClient

# Unit tests
def test_list_campaigns(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.get("/v1/campaigns/test-customer-0")
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, list)
    assert len(content) >= 2
    for item in content:
        assert isinstance(item, dict)
        assert isinstance(item["advertisements"], list)
        assert set(CampaignResponse.model_fields.keys()).issubset(item.keys())

def test_list_visitor_campaigns(db, auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    user_response = visitor_client.get("/v1/auth/me").json()
    user = get_user_by_email(session=db, email=user_response["email"])
    campaigns = retrieve_customer_campaigns(session=db, customer_id=customer.id)
    update_user_input = UpdateUser(email=user.email, role=UserRole.VISITOR, campaign_ids=[campaigns[0].id])
    update_user_customer_link(session=db, user=user, customer=customer, user_input=update_user_input)
    response = visitor_client.get("/v1/campaigns/test-customer-0")
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, list)
    assert len(content) > 0


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.get("/v1/campaigns/test-customer-0")
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.get("/v1/campaigns/test-customer-1")
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.get("/v1/campaigns/test-customer-404")
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.get("/v1/campaigns/test-customer-0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.get("/v1/campaigns/test-customer-0")
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.get("/v1/campaigns/test-customer-0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.get("/v1/campaigns/test-customer-0")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
