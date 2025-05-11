from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.models.campaign import CampaignTargetGender, Advertisement


# Input Schemas
class CreateCampaign(SQLModel):
    """
    Create Campaign Input Format.
    """
    name: str
    announcer: str
    description: Optional[str] = ""
    budget: Optional[float] = None
    budget_currency: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    target_gender: CampaignTargetGender
    target_age_min: int
    target_age_max: int
    target_audience_size: int
    start_date: datetime
    end_date: Optional[datetime] = None
    observation: Optional[str] = None
    advertisements: List[Advertisement] = []  # List of advertisements associated with the campaign


class UpdateCampaign(SQLModel):
    """
    Update Campaign Input Format.
    """
    budget: Optional[float] = None
    target_gender: CampaignTargetGender
    target_age_min: int
    target_age_max: int
    target_audience_size: int
    end_date: Optional[datetime] = None
    advertisements: List[Advertisement]


# Response Schemas
class CampaignResponse(SQLModel):
    id: UUID
    name: str
    announcer: str
    description: Optional[str] = None
    budget: Optional[float] = None
    budget_currency: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    target_gender: CampaignTargetGender
    target_age_min: int
    target_age_max: int
    target_audience_size: int
    last_seen_at: datetime
    start_date: datetime
    end_date: Optional[datetime] = None
    observation: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    advertisements: List[Advertisement]


