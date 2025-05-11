from app.models.user import UserRole, SuperUserRole
from app.schemas.campaigns import CampaignResponse, CreateCampaign
from app.crud.campaign import retrieve_customer_campaigns
from app.crud.customer import get_customer_by_subdomain

from fastapi.testclient import TestClient

# Unit tests
def test_create_incomplete_campaign(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post("/v1/campaigns/test-customer-0", json={
        "name": "Test Create Campaign 1",
        "start_date": "2022-01-01",
        "end_date": "2022-01-02",
        "advertisements": []
    })
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_create_campaign_same_name(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input_1 = create_campaign_input("Test Create Campaign 5")
    campaign_input_2 = create_campaign_input("test create campaign 5")
    response_1 = manager_client.post("/v1/campaigns/test-customer-0", json=campaign_input_1)
    response_2 = manager_client.post("/v1/campaigns/test-customer-0", json=campaign_input_2)
    content = response_2.json()
    assert response_1.status_code == 200
    assert response_2.status_code == 404
    assert isinstance(content, dict)
    assert content["detail"] == "A campaign with this name already exists for that customer."

def test_create_campaign_invalid_name(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = create_campaign_input("Test Create Cãmpañáç")
    response = manager_client.post("/v1/campaigns/test-customer-0", json=campaign_input)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"] == "Invalid campaign name."

def test_create_campaign_invalid_date(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = create_campaign_input("Test Create Campaign 6")
    campaign_input["start_date"] = "2022-02-01"
    campaign_input["end_date"] = "2022-01-01"
    response = manager_client.post("/v1/campaigns/test-customer-0", json=campaign_input)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"] == "Invalid campaign end date."

def test_create_campaign_no_end_date(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = create_campaign_input("Test Create Campaign No End Date")
    campaign_input["end_date"] = None
    response = manager_client.post("/v1/campaigns/test-customer-0", json=campaign_input)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert CampaignResponse(**content)

def test_create_campaign(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = create_campaign_input("Test Create Campaign 7")
    response = manager_client.post("/v1/campaigns/test-customer-0", json=campaign_input)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert CampaignResponse(**content)


# Integration tests
def test_create_campaign_db(db) -> None:
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    campaigns = retrieve_customer_campaigns(session=db, customer_id=customer.id)
    campaign = next((campaign for campaign in campaigns if campaign.name == "Test Create Campaign 7"), None)
    assert campaign.name == "Test Create Campaign 7"
    assert campaign.customer_id == customer.id


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.post("/v1/campaigns/test-customer-0", json=create_campaign_input("Test Create Campaign Auth 1"))
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post("/v1/campaigns/test-customer-1", json=create_campaign_input("Test Create Campaign Auth 2"))
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.post("/v1/campaigns/test-customer-404", json=create_campaign_input("Test Create Campaign Auth 3"))
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.post("/v1/campaigns/test-customer-0", json=create_campaign_input("Test Create Campaign Auth 4"))
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.post("/v1/campaigns/test-customer-0", json=create_campaign_input("Test Create Campaign Auth 5"))
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.post("/v1/campaigns/test-customer-0", json=create_campaign_input("Test Create Campaign Auth 6"))
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.post("/v1/campaigns/test-customer-0", json=create_campaign_input("Test Create Campaign Auth 7"))
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)


# Helper functions
def create_campaign_input(name: str) -> CreateCampaign:
    advertisements = []

    return CreateCampaign(
        name=name,
        announcer="Test Announcer",
        description="Test Description",
        campaign_type="static",
        target_gender="female",
        target_age_min=18,
        target_age_max=50,
        target_audience_size=10000,
        start_date="2022-01-01",
        end_date="2022-02-01",
        advertisements=advertisements
    ).model_dump(mode="json")


