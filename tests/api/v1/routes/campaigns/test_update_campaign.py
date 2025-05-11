import random
from datetime import datetime
import uuid

from app.models.user import UserRole, SuperUserRole
from app.models.campaign import Advertisement
from app.schemas.campaigns import CampaignResponse, UpdateCampaign
from app.crud.campaign import retrieve_customer_campaigns
from app.crud.customer import get_customer_by_subdomain

from fastapi.testclient import TestClient

UPDATE_CAMPAIGN_PATH = lambda id: f"/v1/campaigns/test-customer-0/00000000-0000-0000-0000-000000000{str(id).zfill(3)}"

# Unit tests
def test_update_incomplete_campaign(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1), json={
        "end_date": "2022-01-02",
        "target_gender": "male",
    })
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"][0]["msg"] == "Field required"

def test_update_campaign_invalid_date(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = edit_campaign_input()
    campaign_input["end_date"] = "2020-01-01"
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1), json=campaign_input)
    content = response.json()
    assert response.status_code == 422
    assert isinstance(content, dict)
    assert content["detail"] == "Invalid campaign end date."

def test_update_campaign_no_end_date(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = edit_campaign_input()
    campaign_input["end_date"] = None
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1), json=campaign_input)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert CampaignResponse(**content)

def test_update_campaign(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = edit_campaign_input()
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1), json=campaign_input)
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)
    assert CampaignResponse(**content)


# Integration tests
def test_update_campaign_db(auth_client, db) -> None:
    date_before = datetime.now()
    manager_client = auth_client(UserRole.MANAGER)
    campaign_input = edit_campaign_input()
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1), json=campaign_input)
    content = response.json()
    customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")
    campaigns = retrieve_customer_campaigns(session=db, customer_id=customer.id)
    campaign = next((campaign for campaign in campaigns if campaign.name == "Test Campaign 1"), None)
    assert str(campaign.id) == str(content["id"])
    assert campaign.updated_at > date_before
    assert campaign.last_seen_at > date_before
    assert campaign.target_gender == campaign_input["target_gender"] == content["target_gender"]
    assert campaign.target_age_min == campaign_input["target_age_min"] == content["target_age_min"]
    assert campaign.target_age_max == campaign_input["target_age_max"] == content["target_age_max"]
    assert campaign.target_audience_size == campaign_input["target_audience_size"] == content["target_audience_size"]
    assert campaign.end_date.isoformat() == campaign_input["end_date"] == content["end_date"]


# Authorization tests
def test_non_authenticated_user(client) -> None:
    client = TestClient(client.app)
    response = client.put(UPDATE_CAMPAIGN_PATH(1), json=edit_campaign_input())
    content = response.json()
    assert response.status_code == 401
    assert content["detail"] == "The user is not authenticated."

def test_not_authorized_user(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1).replace("test-customer-0", "test-customer-1"), json=edit_campaign_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user has no access to this customer."

def test_customer_not_found(auth_client) -> None:
    manager_client = auth_client(UserRole.MANAGER)
    response = manager_client.put(UPDATE_CAMPAIGN_PATH(1).replace("test-customer-0", "test-customer-404"), json=edit_campaign_input())
    content = response.json()
    assert response.status_code == 404
    assert content["detail"] == "Customer not found."

def test_analyst_user(auth_client) -> None:
    analyst_client = auth_client(UserRole.ANALYST)
    response = analyst_client.put(UPDATE_CAMPAIGN_PATH(1), json=edit_campaign_input())
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_operation_user(auth_client) -> None:
    operation_client = auth_client(UserRole.OPERATION)
    response = operation_client.put(UPDATE_CAMPAIGN_PATH(1), json=edit_campaign_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_visitor_user(auth_client) -> None:
    visitor_client = auth_client(UserRole.VISITOR)
    response = visitor_client.put(UPDATE_CAMPAIGN_PATH(1), json=edit_campaign_input())
    content = response.json()
    assert response.status_code == 403
    assert content["detail"] == "The user is not allowed to perform this action."

def test_superuser(superuser_client) -> None:
    superuser_client = superuser_client(SuperUserRole.STAFF)
    response = superuser_client.put(UPDATE_CAMPAIGN_PATH(1), json=edit_campaign_input())
    content = response.json()
    assert response.status_code == 200
    assert isinstance(content, dict)


def edit_campaign_input(ad_name="some_ad_name", campaign_id="00000000-0000-0000-0000-000000000001") -> UpdateCampaign:
    advertisements = []
    advertisements.append(Advertisement(name=ad_name+str(random.random()), campaign_id=uuid.UUID(campaign_id)).model_dump(mode="json"))

    return UpdateCampaign(
        target_gender=random.choice(["male", "female", "both"]),
        target_age_min=int(random.random()*10)+18,
        target_age_max=int(random.random()*10)+40,
        target_audience_size=int(random.random()*10000) + 1000,
        end_date=f"2022-02-0{int(random.random()*8)+1}",
        advertisements=advertisements
    ).model_dump(mode="json")

