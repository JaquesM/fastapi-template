from fastapi import APIRouter, Depends

from app.crud.user import get_user_by_email, get_user_by_id, retrieve_user_customer_links
from app.crud.customer import get_customer_by_subdomain
from app.crud.user.user_session import retrieve_user_session_by_refresh_token, update_user_activity, revoke_user_sessions
from app.core.deps import CurrentUser, SessionDep
from app.core import security
from app.schemas import Message
from app.validators.auth import verify_request_user_customer, verify_request_customer, validate_refresh_token
from app.schemas.auth import AuthProvider, RequestAuthInput, CallbackAuthInput, RedirectURLResponse, AccessRefreshTokenResponse, RefreshTokenResponse, MyUserResponse

router = APIRouter()


@router.post("/request/{provider}", response_model=RedirectURLResponse)
async def request_access(
    provider: AuthProvider,
    request_input: RequestAuthInput,
    session: SessionDep
) -> RedirectURLResponse:
    """
    Handles the request for authentication, for the specified provider.

    **Access:** Public access.

    **Args:**
    - `provider (AuthProvider)`: The authentication provider (email, google or microsoft).
    - `request_input (RequestAuthInput)`: Data for the request, such as email, customer_subdomain and callback_url.
    - `session (SessionDep)`: The database session.

    **Returns:**
    - `RedirectURLResponse`: URL to Redirect the user to, in order to authenticate.
    """
    
    # Get the user and the customer from the database
    user = get_user_by_email(session=session, email=request_input.email)
    customer = get_customer_by_subdomain(session=session, customer_subdomain=request_input.customer_subdomain)

    if provider == "email":
        verify_request_user_customer(session=session, user=user, customer=customer)
        return security.request_magic_link(session=session, request_input=request_input, user=user, customer=customer)
    
    elif provider == "google":
        verify_request_customer(customer=customer)
        return security.request_google_auth(request_input=request_input)
    
    elif provider == "microsoft":
        verify_request_customer(customer=customer)
        return security.request_microsoft_auth(request_input=request_input)


@router.post("/callback/{provider}", response_model=AccessRefreshTokenResponse)
async def auth_callback(
    provider: AuthProvider,
    callback_input: CallbackAuthInput,
    session: SessionDep
):
    """
    Handles the callback from the authentication provider.

    **Access:** Public access.

    **Args:**
    - `session (SessionDep)`: The database session.
    - `callback_input (CallbackAuthInput)`: Data for the callback, such as token and customer_subdomain.
    - `provider (AuthProvider)`: The authentication provider (email, google or microsoft).
    
    **Returns:**
    - `AccessRefreshTokenResponse`: The access token and the refresh token generated.
    """

    # Get and verify the customer
    customer = get_customer_by_subdomain(session=session, customer_subdomain=callback_input.customer_subdomain)
    verify_request_customer(customer=customer)

    if provider == "email":
        return security.callback_magic_link(session=session, callback_input=callback_input)
    
    elif provider == "google":
        return await security.callback_google_auth(session=session, callback_input=callback_input, customer=customer)
    
    elif provider == "microsoft":
        return await security.callback_microsoft_auth(session=session, callback_input=callback_input, customer=customer)
        

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(session: SessionDep, token: str = Depends(security.JWTBearer())) -> RefreshTokenResponse:
    """
    Refreshes the access token using a valid refresh token.

    **Args:**
    - `token (str)`: The refresh token provided by the user, passed through Authorization header.

    **Returns:**
    - `RefreshTokenResponse`: The response containing the new access token.
    """
    
    # Validate the refresh token and extract user ID
    user_id = security.verify_refresh_token(token)

    # Get the user session from the database
    db_user_session = retrieve_user_session_by_refresh_token(session=session, refresh_token=token)

    # Check if the token exists in the database and hasn't been used
    validate_refresh_token(user_id=user_id, user_session=db_user_session, refresh_token=token)

    # Update user activity
    update_user_activity(session=session, user_session=db_user_session)

    # Generate new access token
    access_token = security.create_access_token(user_id)

    return RefreshTokenResponse(
        access_token=access_token
    )


@router.get("/me", response_model=MyUserResponse)
async def my_account(current_user: CurrentUser, session: SessionDep) -> MyUserResponse:
    """
    Retrieve the account details of the current user, including linked customers and their details.

    **Access:** User must be authenticated.

    **Returns:**
    - `MyUserResponse`: The response schema containing user account details and linked customers.
    """

    # Get the user from the database
    user = get_user_by_id(session=session, user_id=current_user.id)
    
    # Get the user and user links
    user_links = retrieve_user_customer_links(session=session, user=current_user)
    
    customers_data = [
        MyUserResponse.CustomerLink(
            name=link.customer_name,
            subdomain=link.customer_subdomain,
            status=link.link_status,
            role=link.link_role,
            created_at=link.link_created_at,
            updated_at=link.link_updated_at,
        )
        for link in user_links if link
    ]

    return MyUserResponse(
        email=user.email,
        name=user.name,
        phone=user.phone,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_superuser=user.is_superuser,
        customers=customers_data
    )


@router.post("/signout", response_model=Message)
async def signout_user(session: SessionDep, current_user: CurrentUser) -> Message:
    """
    Signs out the current user by revoking their session.

    **Access:** User must be authenticated.
    
    **Returns:**
    - `Message`: A message indicating the user has been signed out.
    """

    # Revoke all user sessions
    revoke_user_sessions(session=session, user_id=current_user.id)

    return Message(message="User signed out successfully.")

