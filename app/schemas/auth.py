from typing import Optional, List, Literal, Optional
from datetime import datetime
from sqlmodel import SQLModel
from pydantic import ConfigDict


# Types
AuthProvider = Literal["email", "google", "microsoft"]

# Input Schemas
class RequestAuthInput(SQLModel):
    email: Optional[str]
    customer_subdomain: str
    callback_url: Optional[str]

class CallbackAuthInput(SQLModel):
    token: str
    customer_subdomain: Optional[str]
    callback_url: Optional[str]


# Response Schemas
class AccessRefreshTokenResponse(SQLModel):
    access_token: str
    refresh_token: str

class RefreshTokenResponse(SQLModel):
    access_token: str

class RedirectURLResponse(SQLModel):
    redirect_url: str

class MyUserResponse(SQLModel):
    email: str
    name: str
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_superuser: bool
    customers: List['CustomerLink']
    
    class CustomerLink(SQLModel):
        name: str
        subdomain: str
        status: str
        role: str
        created_at: datetime
        updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

