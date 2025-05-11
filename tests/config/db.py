import pytest

from collections.abc import Generator

from sqlalchemy.future import Engine
from sqlmodel import SQLModel, create_engine

from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer
from testcontainers.core import utils

from tests.config.populate_db import populate_test_db


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """
    Setup postgres container
    """
    postgres = PostgresContainer(
        image="postgres:14",
        username="postgres",
        password="test_password",
        dbname="test_database",
        port=5432,
    )
    with postgres:
        wait_for_logs(
            postgres,
            r"UTC \[1\] LOG:  database system is ready to accept connections",
            10,
        )
        yield postgres


@pytest.fixture(scope="session")
def engine(postgres_container) -> Engine:
    """
    Create a single engine instance for the test session
    """
    if utils.is_windows():
        postgres_container.get_container_host_ip = lambda: "localhost"

    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False, future=True)

    # Create tables
    SQLModel.metadata.create_all(engine)

    # Initialize test data
    populate_test_db(engine)

    return engine

