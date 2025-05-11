from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.models.user import UserRole


# Input Schemas
class CreateUser(SQLModel):
    email: str
    name: str
    phone: str
    role: UserRole
    campaign_ids: List[UUID] = []

class UpdateUser(SQLModel):
    role: UserRole
    campaign_ids: List[UUID] = []


# Response Schemas
class UserResponse(SQLModel):
    id: UUID
    email: str
    name: str
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str
    role: str
    campaign_ids: List[UUID] = []
