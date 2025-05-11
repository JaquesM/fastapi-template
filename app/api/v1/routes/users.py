from typing import List

from fastapi import APIRouter

from app.crud.customer import get_customer_by_subdomain
from app.crud import user as crud
from app.core.deps import (
    UserManagerRole,
    SessionDep,
)
from app.schemas.users import UserResponse, CreateUser, UpdateUser
from app.validators.users import validate_create_user_input, validate_update_user_input
from app.exceptions import users as UserExceptions

router = APIRouter()


@router.get("/{customer_subdomain}", response_model=List[UserResponse])
def retrieve_users(
    session: SessionDep,
    customer_subdomain: str,
    current_user: UserManagerRole
) -> List[UserResponse]:
    """
    Retrieve users associated with a specific customer.

    **Access:** Only Manager role.

    **Args:**
    - `customer_subdomain (str)`: The subdomain of the customer whose users are to be retrieved.

    **Returns:**
    - `List[UserResponse]`: A list of users associated with that customer.
    """
    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)
    users = crud.retrieve_users_by_customer_id(session=session, customer_id=customer.id)
    return users


@router.post("/{customer_subdomain}", response_model=UserResponse)
def create_user(
    session: SessionDep,
    customer_subdomain: str,
    user_input: CreateUser,
    current_user: UserManagerRole
) -> UserResponse:
    """
    Create a new user (if necessary) and link them to a customer.

    **Access:** Only Manager role.

    **Args:**
    - `customer_subdomain (str)`: The name of the customer to link the user to.
    - `user_input (CreateUser)`: The input data for creating the user.

    **Returns:**
    - `UserResponse`: The response containing the newly created user.
    """

    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)

    # Validate user input
    validate_create_user_input(session=session, user_input=user_input, customer=customer)

    # Check if a user with this email already exists
    user = crud.get_user_by_email(session=session, email=user_input.email)
    if not user:
        # Create a new User
        user = crud.create_user(session=session, user_input=user_input)

    # Check if user is already connected to that customer
    if (crud.retrieve_user_customer_link(session=session, user=user, customer=customer)):
        raise UserExceptions.UserCustomerLinkAlreadyExistException()
    
    # Create a new UserCustomerLink
    user_link = crud.create_user_customer_link(session=session, user=user, customer=customer, user_input=user_input)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        status=user_link.status,
        role=user_link.role,
        campaign_ids=user_link.campaign_ids,
        created_at=user.created_at,
        updated_at=user_link.updated_at
    )


@router.put("/{customer_subdomain}/{user_id}", response_model=UserResponse)
def update_user_customer_link(
    session: SessionDep,
    customer_subdomain: str,
    user_id: str,
    user_input: UpdateUser,
    current_user: UserManagerRole
) -> UserResponse:
    """
    Updates a User Customer Link.

    **Access:** Only Manager role.

    **Args:**
    - `customer_subdomain (str)`: The name of the customer to link the user to.
    - `user_id (str)`: The id of the user to be edited.
    - `user_input (UpdateUser)`: The input data for updating the user.

    **Returns:**
    - `UserResponse`: The response containing the updated user.
    """

    customer = get_customer_by_subdomain(session=session, customer_subdomain=customer_subdomain)

    # Validate user input
    validate_update_user_input(session=session, user_input=user_input, customer=customer)

    # Check if a user with this email exists
    user = crud.get_user_by_id(session=session, user_id=user_id)
    if not user:
        raise UserExceptions.UserNotFoundException()

    # Check if hte user is connected to that customer
    user_link = crud.retrieve_user_customer_link(session=session, user=user, customer=customer)
    if not user_link:
        raise UserExceptions.UserCustomerLinkNotFoundException()
    
    # Update the UserCustomerLink
    user_link = crud.update_user_customer_link(session=session, user=user, customer=customer, user_input=user_input)

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        status=user_link.status,
        role=user_link.role,
        campaign_ids=user_link.campaign_ids,
        created_at=user.created_at,
        updated_at=user_link.updated_at
    )

