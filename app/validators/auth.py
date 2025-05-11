from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from app.models import UserSession, User, Customer
from app.exceptions import auth as AuthExceptions


def verify_request_user_customer(session: Session, user: User, customer: Customer) -> None:
    """
    Validates the request by checking the provided user and customer details.

    Args:
        session (Session): The database session used for checking user active status.
        user (User): The user object representing the requester.
        customer (Customer): The customer object to which access is being verified.


    Raises:
        CustomerNotFoundException: If the customer object is None.
        UserNotFoundException: If the user object is None.
        UserNotSuperuserException: If the customer is 'admin' and the user is not a superuser.
        UserHasNoAccessToCustomerException: If the user does not have access rights to the customer.
        UserNotActiveException: If the user is not active for the provided customer.
    """
    
    # Make sure the customer and user are valid
    if not customer:
        raise AuthExceptions.CustomerNotFoundException()
    if not user:
        raise AuthExceptions.UserNotFoundException()
    
    # Special condition for 'home' and 'admin' customer
    if customer.subdomain == "home":
        # No specific checks for 'home' customer
        pass
    elif customer.subdomain == "admin":
        if not user.is_superuser:
            raise AuthExceptions.UserNotSuperuserException()
        
    # Verify user access to the customer
    elif not user.has_access_to_customer(customer.id):
        raise AuthExceptions.UserHasNoAccessToCustomerException()
    elif not user.is_active(session, customer.id):
        raise AuthExceptions.UserNotActiveException()
    
    
def verify_request_customer(customer: Customer) -> None:
    # Make sure the customer is valid
    if not customer:
        raise AuthExceptions.CustomerNotFoundException()
    

def validate_refresh_token(user_id: UUID, user_session: UserSession, refresh_token: str) -> None:
    """
    Validates that the provided refresh token is correct and belongs to the user session.

    Args:
        user_id (UUID): The user id.
        user_session (UserSession): The user session of the user.
        refresh_token (str): The refresh token.

    Raises:
        InvalidRefreshTokenException: If the token is invalid.
        TokenNotFoundException: If the token is not found.
        TokenRevokedException: If the token is revoked.
        TokenExpiredException: If the token is expired.
    """

    if not user_id:
        raise AuthExceptions.InvalidRefreshTokenException()
    
    if not user_session or user_session.user_id != UUID(user_id) or user_session.refresh_token != refresh_token:
        raise AuthExceptions.TokenNotFoundException()
    
    if user_session.is_revoked:
        raise AuthExceptions.TokenRevokedException()
    
    if user_session.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise AuthExceptions.TokenExpiredException()
        
