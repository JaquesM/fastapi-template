from sqlalchemy.orm import Session
from app.exceptions import campaigns as CampaignExceptions
from app.schemas.campaigns import CreateCampaign, UpdateCampaign
from app.models import Campaign, Customer
from app.crud.campaign import retrieve_campaign_by_name


def validate_create_campaign_input(session: Session, campaign_input: CreateCampaign, customer: Customer):
    """
    Validates the input for creating a new campaign.
    Args:
        session (Session): The database session to use for queries.
        campaign_input (CreateCampaign): The input data for the new campaign.
        customer (Customer): The customer creating the campaign.
    Raises:
        CampaignExceptions.InvalidCampaignNameException: If the campaign name is less than 3 characters or contains non-ASCII characters.
        CampaignExceptions.CampaignAlreadyExistsException: If a campaign with the same name already exists for the customer.
        CampaignExceptions.InvalidCampaignEndDateException: If the end date is before or the same as the start date.
    """
    # Validate campaign name
    if len(campaign_input.name) < 3 or not campaign_input.name.isascii():
        raise CampaignExceptions.InvalidCampaignNameException()

    if retrieve_campaign_by_name(session=session, customer_id=customer.id, campaign_name=campaign_input.name):
        raise CampaignExceptions.CampaignAlreadyExistsException()

    # Validate campaign dates
    if campaign_input.end_date and campaign_input.end_date <= campaign_input.start_date:
        raise CampaignExceptions.InvalidCampaignEndDateException()


def validate_update_campaign_input(session: Session, campaign_input: UpdateCampaign, customer: Customer, campaign: Campaign):
    """
    Validates the input for updating a campaign.
    Args:
        session (Session): The database session.
        campaign_input (UpdateCampaign): The input data for updating the campaign.
        customer (Customer): The customer associated with the campaign.
        campaign (Campaign): The campaign to be updated.
    Raises:
        CampaignExceptions.CampaignNotFoundException: If the campaign object is not found.
        CampaignExceptions.InvalidCampaignEndDateException: If the campaign end date is invalid.
    """
    # Verify the campaign object
    if not campaign:
        raise CampaignExceptions.CampaignNotFoundException()
            
    # Check if the campaign end date is valid
    if campaign_input.end_date:
        if campaign_input.end_date.replace(tzinfo=None) <= campaign.start_date.replace(tzinfo=None):
            raise CampaignExceptions.InvalidCampaignEndDateException()