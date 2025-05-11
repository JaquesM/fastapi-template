from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select, func

from app.models import Campaign, Customer, Advertisement
from app.schemas.campaigns import CreateCampaign, UpdateCampaign


# Create
def create_campaign(*, session: Session, campaign_input: CreateCampaign, customer: Customer, source_system: str) -> Campaign:
    campaign = Campaign(
        customer_id=customer.id,
        name=campaign_input.name,
        announcer=campaign_input.announcer,
        description=campaign_input.description,
        budget=campaign_input.budget,
        budget_currency=campaign_input.budget_currency,
        city=campaign_input.city,
        country=campaign_input.country,
        target_gender=campaign_input.target_gender,
        target_age_min=campaign_input.target_age_min,
        target_age_max=campaign_input.target_age_max,
        target_audience_size=campaign_input.target_audience_size,
        start_date=campaign_input.start_date,
        end_date=campaign_input.end_date,
        observation=campaign_input.observation,
        source_system=source_system,
        advertisements=[Advertisement(
            campaign_id=ad.campaign_id,
            name=ad.name,
            description=ad.description,
            budget=ad.budget,
        ) for ad in campaign_input.advertisements]
    )
    session.add(campaign)
    session.commit()
    return campaign


# Retrieve
def retrieve_campaign_by_id(*, session: Session, customer_id: UUID, campaign_id: UUID) -> Campaign:
    statement = select(Campaign).where(Campaign.customer_id == customer_id, Campaign.id == campaign_id)
    session_campaign = session.exec(statement).first()
    return session_campaign

def retrieve_campaign_by_name(*, session: Session, customer_id: UUID, campaign_name: str) -> Campaign:
    statement = select(Campaign).where(Campaign.customer_id == customer_id, func.lower(Campaign.name) == campaign_name.lower())
    session_campaign = session.exec(statement).first()
    return session_campaign

def retrieve_customer_campaigns(*, session: Session, customer_id: UUID) -> list[Campaign]:
    statement = select(Campaign).where(Campaign.customer_id == customer_id)
    campaigns = session.exec(statement).all()
    return campaigns


# Update
def update_campaign(*, session: Session, campaign: Campaign, campaign_input: UpdateCampaign) -> Campaign:
    campaign.updated_at = datetime.now()
    campaign.last_seen_at = datetime.now()
    campaign.budget = campaign_input.budget
    campaign.target_gender = campaign_input.target_gender
    campaign.target_age_min = campaign_input.target_age_min
    campaign.target_age_max = campaign_input.target_age_max
    campaign.target_audience_size = campaign_input.target_audience_size
    campaign.end_date = campaign_input.end_date

    for ad in campaign.advertisements:
        if ad not in campaign_input.advertisements:
            session.delete(ad)

    for ad in campaign_input.advertisements:
        if ad not in campaign.advertisements:
            session.add(Advertisement(
                campaign_id=campaign.id,
                name=ad.name,
                description=ad.description,
                budget=ad.budget,
            ))

    session.commit()
    return campaign

def update_campaign_last_seen_at(*, session: Session, campaign: Campaign) -> Campaign:
    campaign.last_seen_at = datetime.now()
    session.commit()
    return campaign


# Delete
def delete_campaign(*, session: Session, campaign: Campaign) -> None:
    # Delete the campaign
    session.delete(campaign)
    session.commit()

