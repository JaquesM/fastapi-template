from datetime import datetime, timezone
from sqlmodel import Session, select

from app.models import UserSession


# Create
def create_user_session(session: Session, user_id: str, refresh_token: str, refresh_token_expires_at: datetime, magic_link_token: str = None, magic_link_expires_at: datetime = None) -> UserSession:
    new_session = UserSession(
        user_id=user_id,
        magic_link_token=magic_link_token,
        magic_link_requested_at=datetime.now(timezone.utc),
        magic_link_expires_at=magic_link_expires_at,
        refresh_token=refresh_token,
        expires_at=refresh_token_expires_at
    )
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    return new_session


# Retrieve
def retrieve_user_sessions_by_user_id(*, session: Session, user_id: str) -> list[UserSession]:
    statement = select(UserSession).where(UserSession.user_id == user_id)
    user_sessions = session.exec(statement).all()
    return user_sessions

def retrieve_active_user_session_by_user_id(*, session: Session, user_id: str) -> UserSession:
    statement = select(UserSession).where(UserSession.user_id == user_id).where(UserSession.is_revoked.is_(False))
    user_sessions = session.exec(statement).first()
    return user_sessions

def retrieve_user_session_by_refresh_token(*, session: Session, refresh_token: str) -> UserSession:
    statement = select(UserSession).where(UserSession.refresh_token == refresh_token)
    user_session = session.exec(statement).first()
    return user_session

def retrieve_user_session_by_magic_link_token(*, session: Session, magic_link_token: str) -> UserSession:
    statement = select(UserSession).where(UserSession.magic_link_token == magic_link_token)
    user_session = session.exec(statement).first()
    return user_session


# Update
def revoke_user_sessions(*, session: Session, user_id: str) -> None:
    previous_sessions = session.exec(
        select(UserSession).where(
            UserSession.user_id == user_id,
            #UserSession.is_revoked == False  # Only find sessions that are not already revoked
        )
    ).all()

    for prev_session in previous_sessions:
        prev_session.is_revoked = True

    session.commit()

def update_user_activity(*, session: Session, user_session: UserSession) -> None:
    user_session.last_used = datetime.now(timezone.utc)
    session.commit()

def update_magic_link_used(*, session: Session, user_session: UserSession) -> None:
    user_session.magic_link_used_at = datetime.now(timezone.utc)
    session.commit()

