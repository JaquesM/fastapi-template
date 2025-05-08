import os
import warnings
from typing import Annotated, Any, Literal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

from pydantic import (
    AnyUrl,
    BeforeValidator,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    ENVIRONMENT: Literal["local", "development", "staging", "production"] = os.getenv("ENVIRONMENT", "local")

    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST")
    BASE_HOST: str = os.getenv("BASE_HOST")

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    MICROSOFT_CLIENT_ID: str = os.getenv("MICROSOFT_CLIENT_ID")
    MICROSOFT_CLIENT_SECRET: str = os.getenv("MICROSOFT_CLIENT_SECRET")

    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER")
    POSTGRES_PORT: int = os.getenv("POSTGRES_PORT")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    EMAILS_FROM_EMAIL: str | None = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: str | None = os.getenv("EMAILS_FROM_NAME", "From Name")

    EMAIL_TEST_USER: str = "test@test.com"


    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        return self

settings = Settings()  # type: ignore
