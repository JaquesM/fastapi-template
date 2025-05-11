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
def request_google_auth(request_input: RequestAuthInput) -> RedirectURLResponse:
    google_auth_url = get_google_auth_url(request_input.callback_url)
    return RedirectURLResponse(redirect_url=google_auth_url)


# Callback
async def callback_google_auth(session: Session, callback_input: CallbackAuthInput, customer: Customer) -> AccessRefreshTokenResponse:
    # Get the user details from Google
    google_user = await get_google_user(callback_input.token, callback_input.callback_url)
    _id, email, _verified_email, _name, _given_name, _family_name, _picture = google_user.values()
    
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


# Helper functions
def get_google_auth_url(redirect_uri: str) -> str:
    google_auth_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&scope=openid%20profile%20email&access_type=offline"
    return google_auth_url

async def get_google_user(code: str, redirect_uri: str) -> dict:
    try:
        # Exchange authorization code for tokens
        token_url = "https://accounts.google.com/o/oauth2/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=data)
            token_response.raise_for_status()
            tokens = token_response.json()

            google_user = await client.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {tokens['access_token']}"})

        return google_user.json()
    except Exception as e:
        logger.error(f"Google OAuth Error: {e}")
        raise AuthExceptions.GoogleOAuthException()

