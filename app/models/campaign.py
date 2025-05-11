import uuid
from datetime import datetime, timezone
from typing import Optional, List

from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint, Index

from app.models import Customer


# Enums
class CampaignTargetGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    BOTH = "both"


# Table models
class Campaign(SQLModel, table=True):
    """
    Represents a campaign entity.
    """
    __tablename__ = "campaigns"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True)
    name: str = Field(max_length=100, nullable=False, index=True)
    announcer: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(default=None, max_length=140)
    budget: Optional[float] = Field(default=None)
    budget_currency: Optional[str] = Field(default=None, max_length=4)
    city: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=50)
    target_gender: CampaignTargetGender = Field(nullable=False)
    target_age_min: int = Field(nullable=False)
    target_age_max: int = Field(nullable=False)
    target_audience_size: int = Field(nullable=False)
    start_date: datetime = Field(nullable=False)
    end_date: Optional[datetime] = Field(default=None)
    observation: Optional[str] = Field(default=None, max_length=140)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    source_system: Optional[str] = Field(default=None, max_length=50)

    # Relationships (back_populates ensures bidirectional linking)
    customer: Optional["Customer"] = Relationship(back_populates="campaigns")
    advertisements: List["Advertisement"] = Relationship(back_populates="campaign", cascade_delete=True)

    __table_args__ = (
        UniqueConstraint("name", "customer_id", name="uq_campaign_name"),
        Index("ix_campaign_customer_id", "customer_id"),
    )


class Advertisement(SQLModel, table=True):
    """
    Represents an advertisement entity.
    """
    __tablename__ = "campaign_advertisements"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    campaign_id: uuid.UUID = Field(foreign_key="campaigns.id", index=True)
    name: str = Field(max_length=100, nullable=False, index=True)
    description: Optional[str] = Field(default=None, max_length=140)
    budget: Optional[float] = Field(default=None)
    target_gender: Optional["CampaignTargetGender"] = Field(default=None)
    target_age_min: Optional[int] = Field(default=None)
    target_age_max: Optional[int] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    observation: Optional[str] = Field(default=None, max_length=140)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    source_system: Optional[str] = Field(default=None, max_length=50)

    # Relationships (back_populates ensures bidirectional linking)
    campaign: "Campaign" = Relationship(back_populates="advertisements")

    __table_args__ = (
        UniqueConstraint("name", "campaign_id", name="uq_advertisement_name"),
        Index("ix_advertisement_campaign_id", "campaign_id"),
    )

