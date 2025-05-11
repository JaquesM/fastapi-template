from typing import List

from fastapi import APIRouter
from sqlalchemy.exc import IntegrityError

from app.core.deps import UserAnalystRole, UserVisitorRole, SessionDep
from app.crud import campaign as crud
from app.crud.customer import get_customer_by_subdomain
from app.validators.campaigns import validate_create_campaign_input, validate_update_campaign_input
from app.models import UserRole
from app.schemas.campaigns import CampaignResponse, CreateCampaign, UpdateCampaign
from app.schemas import Message
from app.exceptions import campaigns as CampaignExceptions
from app.services.monitoring import logger

router = APIRouter()


@router.get("/{customer_subdomain}", response_model=List[CampaignResponse])
def retrieve_campaigns(
    session: SessionDep,
    customer_subdomain: str,
    current_user: UserVisitorRole
) -> List[CampaignResponse]:
    """
    Retrieve a list of campaigns for a given customer.

    **Access:** Manager, Analyst, and some Visitor roles.

    **Args:**
    - `customer_subdomain (str)`: The subdomain of the customer whose campaigns are to be retrieved.

    **Returns:**
    - `List[CampaignResponse]`: A list of campaigns associated with the customer.
    """

    # Get customer
    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)

    # Get all campaigns of the customer
    campaigns = crud.retrieve_customer_campaigns(session=session, customer_id=customer.id)

    # Filter campaigns for visitor role
    if hasattr(current_user, 'role') and current_user.role == UserRole.VISITOR:
        campaigns = [campaign for campaign in campaigns if current_user.campaign_ids and campaign.id in current_user.campaign_ids]

    return [CampaignResponse.model_validate(campaign) for campaign in campaigns]


@router.post("/{customer_subdomain}", response_model=CampaignResponse)
def create_campaign(
    session: SessionDep,
    campaign_input: CreateCampaign,
    customer_subdomain: str,
    current_user: UserAnalystRole
) -> CampaignResponse:
    """
    Create a new campaign for a specified customer.

    **Access:** Manager and Analyst roles.

    **Args:**
    - `campaign_input (CreateCampaign)`: The campaign details.
    - `customer_subdomain (str)`: The subdomain of the customer.

    **Returns:**
    - `CampaignResponse`: The newly created campaign.
    """

    # Get customer
    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)

    # Validate campaign input
    validate_create_campaign_input(session=session, campaign_input=campaign_input, customer=customer)
        
    # Create a new campaign
    try:
        campaign = crud.create_campaign(session=session, campaign_input=campaign_input, customer=customer, source_system="Created by user")
        return CampaignResponse.model_validate(campaign)
    
    except IntegrityError as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise CampaignExceptions.CampaignAlreadyExistsException()
        raise e
    
    except Exception as e:
        logger.error(e)
        raise CampaignExceptions.CouldNotCreateCampaignException()


@router.put("/{customer_subdomain}/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    session: SessionDep,
    campaign_input: UpdateCampaign,
    customer_subdomain: str,
    current_user: UserAnalystRole,
    campaign_id: str
) -> CampaignResponse:
    """
    Update a campaign data.

    **Access:** Manager and Analyst.

    **Args:**
    - `campaign_input (UpdateCampaign)`: The campaign changes.
    - `customer_subdomain (str)`: The subdomain of the customer.
    - `campaign_id (UUID)`: The id of the campaign.

    **Returns:**
    - `CampaignResponse`: The edited campaign.
    """

    # Get customer
    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)

    # Get the campaign object
    campaign = crud.retrieve_campaign_by_id(session=session, customer_id=customer.id, campaign_id=campaign_id)
    
    # Validate campaign input
    validate_update_campaign_input(session=session, campaign_input=campaign_input, customer=customer, campaign=campaign)

    # Update campaign
    campaign = crud.update_campaign(session=session, campaign=campaign, campaign_input=campaign_input)
  
    return campaign


@router.delete("/{customer_subdomain}/{campaign_id}", response_model=Message)
def delete_campaign(
    session: SessionDep,
    customer_subdomain: str,
    current_user: UserAnalystRole,
    campaign_id: str
) -> Message:
    """
    Delete a campaign by name.

    **Access:** Manager and Analyst.

    **Args:**
    - `customer_subdomain (str)`: The subdomain of the customer.
    - `campaign_id (UUID)`: The id of the campaign.

    **Returns:**
    - `Message`: Message contaning the following message: `Campaign deleted successfully`.
    """

    # Get customer
    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)

    # Get the campaign object
    campaign = crud.retrieve_campaign_by_id(session=session, customer_id=customer.id, campaign_id=campaign_id)
    if not campaign:
        raise CampaignExceptions.CampaignNotFoundException()

    # Delete campaign
    crud.delete_campaign(session=session, campaign=campaign)

    return Message(message="Campaign deleted successfully.")
