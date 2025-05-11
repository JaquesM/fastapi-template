from datetime import datetime, timedelta, timezone
from typing import Any
import jwt

from app.core.config import settings


ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 30


# Access Token
def create_access_token(subject: str | Any, expires_delta: timedelta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: str | Any, expires_delta: timedelta = timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)):
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Refresh Token
def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception: # as e:
        return None

