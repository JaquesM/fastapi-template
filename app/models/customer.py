import uuid
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from .user import UserCustomerLink
from datetime import datetime, timezone
from typing import Optional, List


# Table models
class Customer(SQLModel, table=True):
    """
    Represents a customer entity.
    """
    __tablename__ = "customers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=100)
    subdomain: str = Field(max_length=100)
    contact_email: Optional[str] = Field(max_length=100)
    contact_phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=140)
    observation: Optional[str] = Field(default=None, max_length=140)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_system: Optional[str] = Field(default=None, max_length=50)

    # Relationships
    access_keys: List["CustomerAccessKey"] = Relationship(back_populates="customer", cascade_delete=True)
    users: List["User"] = Relationship(back_populates="customers", link_model=UserCustomerLink)
    campaigns: List["Campaign"] = Relationship(back_populates="customer")

    __table_args__ = (
        UniqueConstraint("name", name="uq_customer_name"),
        UniqueConstraint("subdomain", name="uq_customer_subdomain")
    )


class CustomerAccessKey(SQLModel, table=True):
    """
    API access key for a customer.
    """
    __tablename__ = "customer_access_keys"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(max_length=64, unique=True, index=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None)
    last_used_at: Optional[datetime] = Field(default=None)

    # Relationship
    customer: Customer = Relationship(back_populates="access_keys")

