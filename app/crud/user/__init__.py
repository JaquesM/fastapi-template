from datetime import datetime
from sqlmodel import Session, select

from app.models import User, UserCustomerLink, Customer
from app.schemas.users import UserResponse, CreateUser, UpdateUser


# Create
def create_user(*, session: Session, user_input: CreateUser) -> User:
    user = User(
        email=user_input.email,
        name=user_input.name,
        phone=user_input.phone,  
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def create_user_customer_link(*, session: Session, user: User, customer: Customer, user_input: CreateUser) -> UserCustomerLink:
    user_link = UserCustomerLink(
        user_id=user.id,
        customer_id=customer.id,
        role=user_input.role,
        campaign_ids=user_input.campaign_ids
    )
    session.add(user_link)
    session.commit()
    session.refresh(user_link)
    return user_link


# Retrieve
# - Getters
def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user

def get_user_by_id(*, session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user

def retrieve_users_by_customer_id(*, session: Session, customer_id: int) -> list[UserResponse]:
    query = (
        select(
            User.id,
            User.email,
            User.name,
            User.phone,
            User.created_at,
            UserCustomerLink.status,
            UserCustomerLink.role,
            UserCustomerLink.campaign_ids,
            UserCustomerLink.updated_at,
        )
        .join(UserCustomerLink, UserCustomerLink.user_id == User.id)
        .where(UserCustomerLink.customer_id == customer_id)
        .order_by(User.created_at.desc())
    )
    rows = session.exec(query).all()
    users = [
        UserResponse(
            id=row.id,
            email=row.email,
            name=row.name,
            phone=row.phone,
            status=row.status,
            role=row.role,
            campaign_ids=row.campaign_ids,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]
    return users

def retrieve_user_customer_link(*, session: Session, user: User, customer: Customer) -> UserCustomerLink | None:
    query = (
        select(
            UserCustomerLink
        )
        .where((UserCustomerLink.user_id == user.id) & (UserCustomerLink.customer_id == customer.id))
    )
    user_link = session.exec(query).first()    
    return user_link

def retrieve_user_customer_links(*, session: Session, user: User) -> list[UserCustomerLink]:
    query = (
        select(
            User.id,
            Customer.id.label('customer_id'),
            Customer.name.label('customer_name'),
            Customer.subdomain.label('customer_subdomain'),
            UserCustomerLink.status.label('link_status'),
            UserCustomerLink.role.label('link_role'),
            UserCustomerLink.created_at.label('link_created_at'),
            UserCustomerLink.updated_at.label('link_updated_at'),
        )
        .join(UserCustomerLink, UserCustomerLink.user_id == User.id)
        .join(Customer, UserCustomerLink.customer_id == Customer.id)
        .where(UserCustomerLink.user_id == user.id)
    )
    user_links = session.exec(query).all()
    return user_links

# Update
def update_user_customer_link(*, session: Session, user: User, customer: Customer, user_input: UpdateUser) -> User:
    user_link = retrieve_user_customer_link(session=session, user=user, customer=customer)
    user_link.campaign_ids = user_input.campaign_ids
    user_link.role = user_input.role
    user_link.updated_at = datetime.now()
    session.commit()
    return user_link


