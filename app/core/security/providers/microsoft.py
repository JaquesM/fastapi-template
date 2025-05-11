import httpx
from datetime import datetime, timedelta, timezone
from sqlmodel import Session

from app.core.config import settings
from app.core.security.token import create_access_token, create_refresh_token, JWT_REFRESH_TOKEN_EXPIRE_DAYS
from app.exceptions import auth as AuthExceptions
from app.services.monitoring import logger
from app.models import Customer
from app.schemas.auth import RequestAuthInput, CallbackAuthInput, RedirectURLResponse, AccessRefreshTokenResponse
from app.crud.user import get_user_by_email
from app.crud.user.user_session import revoke_user_sessions, create_user_session
from app.validators.auth import verify_request_user_customer


# Request
def request_microsoft_auth(request_input: RequestAuthInput) -> RedirectURLResponse:
    microsoft_auth_url = get_microsoft_auth_url(request_input.callback_url)
    return RedirectURLResponse(redirect_url=microsoft_auth_url)


# Callback
async def callback_microsoft_auth(session: Session, callback_input: CallbackAuthInput, customer: Customer) -> AccessRefreshTokenResponse:
    # Get the user details from Microsoft
    microsoft_user = await get_microsoft_user(callback_input.token, callback_input.callback_url)
    if "error" in microsoft_user:
        raise AuthExceptions.MicrosoftOAuthException()
    
    email = microsoft_user.get("mail")
    
    # Get the user from the database
    user = get_user_by_email(session=session, email=email)

    # Verify the user and customer
    verify_request_user_customer(session=session, user=user, customer=customer)
    
    # Generate refresh token
    refresh_token = create_refresh_token(user.id)
    refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # Handle the user sessions
    revoke_user_sessions(session=session, user_id=user.id)
    new_session = create_user_session(session=session, user_id=user.id, refresh_token=refresh_token, refresh_token_expires_at=refresh_token_expires_at)

    # Create JWT access token
    access_token = create_access_token(user.id)
    
    return AccessRefreshTokenResponse(
        access_token=access_token,
        refresh_token=new_session.refresh_token
    )


# Helper function
def get_microsoft_auth_url(redirect_uri: str) -> str:
    auth_url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    microsoft_auth_url = (
        f"{auth_url}?client_id={settings.MICROSOFT_CLIENT_ID}"
        f"&response_type=code&redirect_uri={redirect_uri}"
        f"&response_mode=query&&scope=https%3A%2F%2Fgraph.microsoft.com%2FUser.Read%20openid%20email%20profile&state=12345"
    )
    return microsoft_auth_url

async def get_microsoft_user(code: str, redirect_uri: str) -> dict:
    try:
        # Exchange authorization code for tokens
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": settings.MICROSOFT_CLIENT_ID,
            "client_secret": settings.MICROSOFT_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=data)
            token_response.raise_for_status()
            tokens = token_response.json()

            microsoft_user = await client.get("https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})

        return microsoft_user.json()
    except Exception as e:
        logger.error(f"Microsoft OAuth Error: {e}")
        raise AuthExceptions.MicrosoftOAuthException()


