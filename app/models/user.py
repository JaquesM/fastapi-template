import uuid
import re
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, SQLModel, Session
from sqlalchemy import Column, Enum as SQLAlchemyEnum, UniqueConstraint, Index, select
from sqlalchemy.dialects.postgresql import ARRAY, UUID


# Enums
class UserRole(str, Enum):
    MANAGER    = "MANAGER"      # User Manager      -  Full access to customer dashboard, can add users and devices
    ANALYST    = "ANALYST"      # User Analyst      -  Access to all customer metrics
    OPERATION  = "OPERATION"    # User Operator     -  Limited access to the devices panel
    VISITOR    = "VISITOR"      # User Visitor      -  Restricted access only to allowed campaigns

class SuperUserRole(str, Enum):
    ADMIN      = "ADMIN"        # Superuser Admin       -  Full Access to everything
    STAFF      = "STAFF"        # Superuser Staff       -  Access to some parts of Admin Dashboard and Customer Dashboards


# Link Models
class UserCustomerLink(SQLModel, table=True):
    """
    Represents the relationship between campaigns and devices.
    """
    __tablename__ = "user_customer_links"

    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    customer_id: uuid.UUID = Field(foreign_key="customers.id", primary_key=True)
    role: UserRole = Field(sa_column=Column(SQLAlchemyEnum(UserRole)))
    campaign_ids: List[uuid.UUID] = Field(sa_column=Column(ARRAY(UUID)), default_factory=list)
    status: str = Field(default="active", max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "customer_id", name="uq_user_customer"),
    )



# Table Models
class User(SQLModel, table=True):
    """
    Represents a user entity.
    """
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True)
    name: str = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_superuser: bool = Field(default=False)
    superuser_role: Optional[SuperUserRole] = Field(sa_column=Column(SQLAlchemyEnum(SuperUserRole)), default=None)

    # Relationships
    sessions: List["UserSession"] = Relationship(back_populates="user")
    customers: List["Customer"] = Relationship(back_populates="users", link_model=UserCustomerLink)

    # Constraints
    __table_args__ = (
        UniqueConstraint("email", name="uq_user_email"),
    )


    def has_access_to_customer(self, customer_id: uuid.UUID) -> bool:
        """Check if the user has access to a given customer by id."""
        # Superuser has access to all customers
        if self.is_superuser:
            return True
        
        # Check if the user has access to the customer
        for customer in self.customers:
            if customer.id == customer_id:
                return True

            
        return False

    def is_active(self, session: Session, customer_id: uuid.UUID) -> bool:
        """Check if the user is active for this customer in the system."""
        # Superuser is always active
        if self.is_superuser:
            return True
        
        # Check if the user has access to the customer
        user_customer_link = session.exec(select(UserCustomerLink).where(UserCustomerLink.user_id == self.id and UserCustomerLink.customer_id == customer_id)).scalars().first()

        if user_customer_link:
            return user_customer_link.status == "active"
        
        return False


class UserSession(SQLModel, table=True):
    """
    Represents the user session after signin.
    """
    __tablename__ = "user_sessions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    refresh_token: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_revoked: bool = Field(default=False)

    magic_link_token: Optional[str] = Field(default=None)
    magic_link_requested_at: Optional[datetime] = Field(default=None)
    magic_link_expires_at: Optional[datetime] = Field(default=None)
    magic_link_used_at: Optional[datetime] = Field(default=None)

    user: "User" = Relationship(back_populates="sessions")


