from collections.abc import Generator
from typing import Annotated, List, Callable
import jwt
from functools import partial
from fastapi import Depends
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.core.security.token import ALGORITHM
from app.crud.customer import get_customer_by_subdomain
from app.crud.user.user_session import retrieve_active_user_session_by_user_id
from app.schemas.auth import TokenPayload
from app.models import User, UserCustomerLink
from app.models.user import UserRole
from app.exceptions import auth as AuthExceptions


# DB Session Dependency
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_db)]


# Token Dependency
oauth2_scheme = security.JWTBearer()
TokenDep = Annotated[str, Depends(oauth2_scheme)]


# Current User Dependency
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise AuthExceptions.InvalidTokenException()
    
    user = session.get(User, token_data.sub)
    if not user:
        raise AuthExceptions.UserNotFoundException()
    if not retrieve_active_user_session_by_user_id(session=session, user_id=user.id):
        raise AuthExceptions.UserNotAuthenticatedException()
    return user
CurrentUser = Annotated[User, Depends(get_current_user)]


# Customer Role User Dependency
def customer_role_user_dependency(session: SessionDep, current_user: CurrentUser, customer_subdomain: str, required_role: List[UserRole]) -> User:
    # Check if the customer exists
    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)
    if not customer:
        raise AuthExceptions.CustomerNotFoundException()

    if current_user.is_superuser:
        return current_user

    # Get the UserCustomerLink for the current user and the customer
    customer_link = session.exec(select(UserCustomerLink).where((UserCustomerLink.user_id == current_user.id) & (UserCustomerLink.customer_id == customer.id))).first()
    if not customer_link:
        raise AuthExceptions.UserHasNoAccessToCustomerException()
    
    # Check if the user is active for this customer in the system
    if customer_link.status != "active":
        raise AuthExceptions.UserNotActiveException()

    # Check if the user has the required role for the customer
    if len(required_role)>0 and customer_link.role not in required_role:
        raise AuthExceptions.UserActionNotAllowedException()
    
    return customer_link

# All Role Dependencies
def role_dependency(required_role: List[UserRole]) -> Callable:
    """
    Factory to create a dependency that validates a user's role for a customer.
    """
    def dependency(
        session: SessionDep,
        current_user: CurrentUser,
        customer_subdomain: str,
    ) -> UserCustomerLink:
        return customer_role_user_dependency(
            session=session,
            current_user=current_user,
            customer_subdomain=customer_subdomain,
            required_role=required_role,
        )

    return dependency
UserAnyRole = Annotated[UserCustomerLink, Depends(role_dependency([]))]
UserManagerRole = Annotated[UserCustomerLink, Depends(role_dependency([UserRole.MANAGER]))]
UserAnalystRole = Annotated[UserCustomerLink, Depends(role_dependency([UserRole.ANALYST, UserRole.MANAGER]))]
UserOperationRole = Annotated[UserCustomerLink, Depends(role_dependency([UserRole.OPERATION, UserRole.MANAGER]))]
UserVisitorRole = Annotated[UserCustomerLink, Depends(role_dependency([UserRole.VISITOR, UserRole.ANALYST, UserRole.MANAGER]))]


# Superuser Dependency
def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise AuthExceptions.UserNotSuperuserException()
    return current_user
CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]

