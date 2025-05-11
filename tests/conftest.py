from fastapi.testclient import TestClient
from sqlmodel import Session as SQLSession
import pytest

from collections.abc import Generator

from app.core.deps import get_db
from app.models import UserRole, SuperUserRole
from app.main import app

# Database fixtures - DONT REMOVE
from .config.db import postgres_container, engine
from .config.auth import auth_token, create_user
# Database fixtures - DONT REMOVE


# Database Session
@pytest.fixture(scope="session")
def db(engine) -> Generator[SQLSession, None, None]:
    """
    Provide a test database for the testing process each test case
    """    
    with SQLSession(engine) as session:
        yield session


# Clients
@pytest.fixture(scope="session")
def client(engine) -> Generator[TestClient, None, None]:
    """
    Create a test client with an overridden database dependency
    """
    # Override the database dependency with the test database
    def override_get_db():
        with SQLSession(engine) as session:
            yield session

    # Apply override to main app
    app.dependency_overrides[get_db] = override_get_db

    # Apply override to each subapp
    # If you have multiple sub-apps, you should override them here as well

    # Yield the test client with the overridden database dependency
    with TestClient(app) as c:
        yield c

    # Clear the database dependency override
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def auth_client(client, auth_token) -> Generator[TestClient, None, None]:
    """Returns a test client with automatic authentication headers."""
    def _auth_client(role: UserRole, is_superuser: bool = False, superuser_role: SuperUserRole = None):
        token = auth_token(role, is_superuser, superuser_role)
        
        # Create a new independent client instance
        auth_client_instance = TestClient(client.app)  
        auth_client_instance.headers.update({"Authorization": token})
        
        return auth_client_instance
    
    return _auth_client


@pytest.fixture(scope="session")
def superuser_client(client, auth_token) -> Generator[TestClient, None, None]:
    """Returns a test client with automatic authentication headers."""
    def _superuser_client(superuser_role: SuperUserRole):
        token = auth_token(None, True, superuser_role)
        
        # Create a new independent client instance
        auth_client_instance = TestClient(client.app)  
        auth_client_instance.headers.update({"Authorization": token})
        
        return auth_client_instance
    
    return _superuser_client

