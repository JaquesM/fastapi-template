import re
from sqlalchemy.orm import Session
from app.exceptions import users as UserExceptions, campaigns as CampaignExceptions
from app.schemas.users import CreateUser, UpdateUser
from app.models import Customer, UserRole
from app.crud.campaign import retrieve_customer_campaigns


def validate_create_user_input(session: Session, user_input: CreateUser, customer: Customer) -> None:
    """
    Validates the input provided for creating a new user.
    Args:
        session (Session): The database session.
        user_input (CreateUser): The input data for the new user.
        customer (Customer): The customer to which the user will be associated.
    Raises:
        UserExceptions.InvalidUserNameException: If the 'name' attribute is shorter than 3 characters or contains non-ASCII characters.
        UserExceptions.InvalidUserRoleRequirementsException: If the user's role is 'VISITOR' and no campaign IDs are provided.
        CampaignExceptions.CampaignNotAssociatedException: If any campaign ID in the update input is not linked to the customer.
    """
    # Validate campaign name
    if len(user_input.name) < 3 or not user_input.name.isascii():
        raise UserExceptions.InvalidUserNameException()
    
    # Validate email format
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_input.email):
        raise UserExceptions.InvalidUserEmailException()
    
    # Validate role requirements
    if user_input.role == UserRole.VISITOR:
        if len(user_input.campaign_ids) == 0:
            raise UserExceptions.InvalidUserRoleRequirementsException()

        # Validate campaign association
        customer_campaigns = retrieve_customer_campaigns(session=session, customer_id=customer.id)
        customer_campaign_ids = [campaign.id for campaign in customer_campaigns]
        for campaign_id in user_input.campaign_ids:
            if campaign_id not in customer_campaign_ids:
                raise CampaignExceptions.CampaignNotAssociatedException()


def validate_update_user_input(session: Session, user_input: UpdateUser, customer: Customer) -> None:
    """
    Validates the input provided for updating a user.
    Args:
        session (Session): The database session.
        user_input (UpdateUser): The input data for the updated user.
        customer (Customer): The customer to which the user will be associated.
    Raises:
        UserExceptions.InvalidUserRoleRequirementsException: If the user's role is 'VISITOR' and no campaign IDs are provided.
        CampaignExceptions.CampaignNotAssociatedException: If any campaign ID in the update input is not linked to the customer.
    """
    # Validate role requirements
    if user_input.role == UserRole.VISITOR:
        if len(user_input.campaign_ids) == 0:
            raise UserExceptions.InvalidUserRoleRequirementsException()

        # Validate campaign association
        customer_campaigns = retrieve_customer_campaigns(session=session, customer_id=customer.id)
        customer_campaign_ids = [campaign.id for campaign in customer_campaigns]
        for campaign_id in user_input.campaign_ids:
            if campaign_id not in customer_campaign_ids:
                raise CampaignExceptions.CampaignNotAssociatedException()

