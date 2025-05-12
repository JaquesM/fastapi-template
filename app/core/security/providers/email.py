from datetime import datetime, timedelta, timezone
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import SignatureExpired, BadSignature
from sqlmodel import Session

from app.core.config import settings
from app.schemas.auth import RequestAuthInput, CallbackAuthInput, RedirectURLResponse, AccessRefreshTokenResponse
from app.models import User, Customer
from app.services.email import generate_magic_link_email, send_email
from app.crud.user.user_session import create_user_session, retrieve_user_session_by_magic_link_token, update_magic_link_used, revoke_user_sessions
from app.crud.user import get_user_by_email
from app.core.security.token import create_access_token, create_refresh_token, JWT_REFRESH_TOKEN_EXPIRE_DAYS
from app.exceptions.auth import TokenExpiredException, InvalidTokenException, TokenNotFoundException

MAGIC_LINK_TOKEN_EXPIRE_MINUTES = 15

serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


# Request
def request_magic_link(session: Session, request_input: RequestAuthInput, user: User, customer: Customer) -> RedirectURLResponse:
    """
    Sends a magic link token email for the given user email address.

    Args:
        session (Session): The database session.
        request_input (RequestAuthInput): The request input containing the email address.
        user (User): The user object.
        customer (Customer): The customer object.

    Returns:
        Message: A successfull response.
    """

    # Generate magic link token
    magic_link_token = generate_magic_link_token(request_input.email)
    magic_link_expires_at = datetime.now(timezone.utc) + timedelta(minutes=MAGIC_LINK_TOKEN_EXPIRE_MINUTES)

    # Generate refresh token
    refresh_token = create_refresh_token(user.id)
    refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # Handle the user sessions
    revoke_user_sessions(session=session, user_id=user.id)
    _user_session = create_user_session(session=session, user_id=user.id, refresh_token=refresh_token, refresh_token_expires_at=refresh_token_expires_at, magic_link_token=magic_link_token, magic_link_expires_at=magic_link_expires_at)

    # Generate magic link email
    magic_link_email = generate_magic_link_email(
        customer.name,
        user.name,
        request_input.callback_url+magic_link_token,
        MAGIC_LINK_TOKEN_EXPIRE_MINUTES
    )

    # Send email with magic link
    send_email(
        email_to=user.email,
        subject=magic_link_email.subject,
        html_content=magic_link_email.html_content
    )

    return RedirectURLResponse(redirect_url="Magic link email sent")


# Callback
def callback_magic_link(session: Session, callback_input: CallbackAuthInput) -> AccessRefreshTokenResponse:
    """
    Callback function to handle the magic link token verification.

    Args:
        session (Session): The database session.
        callback_input (CallbackAuthInput): Data for the request, such as email, customer_subdomain and callback_url.

    Returns:
        AccessRefreshTokenResponse: A response with the access key and refresh key.
    """

    # Verify the magic link token
    try:
        email = verify_magic_link_token(callback_input.token)
    except SignatureExpired:
        raise TokenExpiredException()
    except BadSignature:
        raise InvalidTokenException()
    
    # Get the user from the database
    user = get_user_by_email(session=session, email=email)

    # Check if the token exists in the database and hasn't been used
    user_session = retrieve_user_session_by_magic_link_token(session=session, magic_link_token=callback_input.token)
    if not user_session or user_session.user_id != user.id:
        raise TokenNotFoundException()
    #elif db_user_session.magic_link_used_at:
    #    raise TokenHasBeenUsedException()
    elif user_session.magic_link_expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise TokenExpiredException()

    # Mark token as used
    update_magic_link_used(session=session, user_session=user_session)

    # Generate access token
    access_token = create_access_token(user.id)

    return AccessRefreshTokenResponse(
        access_token=access_token,
        refresh_token=user_session.refresh_token
    )


# Helper functions
def generate_magic_link_token(email: str) -> str:
    return serializer.dumps(email, salt="$ome$alt")

def verify_magic_link_token(token: str) -> str:
    return serializer.loads(token, salt="$ome$alt", max_age=MAGIC_LINK_TOKEN_EXPIRE_MINUTES*60)

