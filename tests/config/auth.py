import pytest

from datetime import date, timedelta
from collections.abc import Generator

from app.models import User, UserCustomerLink, UserSession, SuperUserRole, UserRole
from app.core import security
from app.core.security.providers.email import generate_magic_link_token
from app.crud.customer import get_customer_by_subdomain

from .utils import random_string

@pytest.fixture(scope="session")
def create_user(db) -> Generator[User, None, None]:
    """
    Factory function to create a user and link it to a customer in the database.
    """
    def _create_user(role: UserRole, is_superuser: bool = False, superuser_role: SuperUserRole = None):
        user = User(
            name=random_string(8),
            email=f"{random_string(12)}@email.com",
            is_superuser=is_superuser,
            superuser_role=superuser_role,
        )
        db.add(user)
        db.add(UserSession(
            user_id=user.id,
            refresh_token="token",
            expires_at=date.today() + timedelta(days=10),
            magic_link_token=generate_magic_link_token(user.email),
            magic_link_requested_at=date.today(),
            magic_link_expires_at=date.today() + timedelta(days=100),
        ))
        db.commit()
        db.refresh(user)

        if not is_superuser:        
            # Link the user to a customer
            customer = get_customer_by_subdomain(session=db, customer_subdomain="test-customer-0")

            user_customer_link = UserCustomerLink(
                user_id=user.id,
                customer_id=customer.id,
                role=role,
            )
            db.add(user_customer_link)
            db.commit()
        
        return user
    return _create_user


@pytest.fixture(scope="session")
def auth_token(create_user):
    """
    Factory function to generate JWT tokens for different roles.
    """
    def _auth_token(role: UserRole, is_superuser: bool = False, superuser_role: SuperUserRole = None):
        user = create_user(role, is_superuser, superuser_role)
        access_token = security.create_access_token(user.id)
        return f"Bearer {access_token}"
    return _auth_token


