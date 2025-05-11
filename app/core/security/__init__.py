from typing import Optional
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from app.exceptions import auth as AuthExceptions

# Providers
from .providers.email import request_magic_link, callback_magic_link
from .providers.google import request_google_auth, callback_google_auth
from .providers.microsoft import request_microsoft_auth, callback_microsoft_auth

# Other
from .token import create_access_token, create_refresh_token, verify_refresh_token

# OAuth2-like Bearer Token for Dependency Injection
class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise AuthExceptions.UserNotAuthenticatedException()
            else:
                return None
        return param


