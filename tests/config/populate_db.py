from uuid import uuid4, UUID
from typing import List
from datetime import date, timedelta
import random
from sqlmodel import Session as SQLSession

from app.models import Customer, User, UserCustomerLink, UserSession, UserRole, Campaign
from app.core.security.providers.email import generate_magic_link_token
from app.core.security.token import create_refresh_token

def populate_test_db(engine) -> None:
    """
    Populate the test database with some sample data
    """
    with SQLSession(engine) as session:
        # Create test customers
        customer_ids = create_customers(session)
        session.commit()

        # Create test users
        create_users(session, customer_ids)
        session.commit()

        # Create test campaigns
        create_campaigns(session, customer_ids)
        session.commit()


# Mock data creation functions
def create_customers(session: SQLSession) -> List[UUID]:
    # Test customers
    customer_ids = []
    for i in range(3):
        new_customer_id = uuid4()
        customer_ids.append(new_customer_id)
        customer = Customer(
            id=new_customer_id,
            name=f"Test Customer {i}",
            subdomain=f"test-customer-{i}",
        )
        session.add(customer)

    # Demo customer
    new_customer_id = uuid4()
    customer_ids.append(new_customer_id)
    session.add(Customer(
        id=new_customer_id,
        name="Demo",
        subdomain="demo",
    ))

    return customer_ids

def create_users(session: SQLSession, customer_ids: List[UUID]) -> None:
    get_user_id = lambda i: f"00000000-0000-0000-0000-00000000000{i}"
    
    # Create test users
    for i in range(0, 10):
        session.add(User(
            id=get_user_id(i),
            email=f"test_user_{i}@email.com",
            name=f"Test User {i}",
        ))
    session.flush()

    # Create test user-customer links
    session.add(UserCustomerLink(
        user_id=get_user_id(0),
        customer_id=customer_ids[0],
        role=UserRole.MANAGER,
        status="active",
    ))
    
    # Create test user-sessions
    for i in range(0, 10):
        session.add(UserSession(
            user_id=get_user_id(i),
            refresh_token=create_refresh_token(get_user_id(i)),
            expires_at=date.today() + timedelta(days=10),
            magic_link_token=generate_magic_link_token(f"test_user_{i}@email.com"),
            magic_link_requested_at=date.today(),
            magic_link_expires_at=date.today() + timedelta(days=100),
            is_revoked=i < 5,
        ))

def create_campaigns(session: SQLSession, customer_ids: List[UUID]) -> None:
    for i in [1, 101, 102, 103, 104, 1000]:
        session.add(Campaign(
            id=f"00000000-0000-0000-0000-00000000{str(i).zfill(4)}",
            customer_id=customer_ids[0 if i < 1000 else -1],
            name=f"Test Campaign {i}",
            announcer="Test Announcer",
            description="Test Description",
            start_date="2021-01-01",
            end_date="2021-01-31",
            budget=1000,
            target_gender="male",
            target_age_min=18,
            target_age_max=35,
            target_audience_size=10000,
            advertisements=[]
        ))
