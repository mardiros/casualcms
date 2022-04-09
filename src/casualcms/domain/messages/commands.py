import secrets
import uuid
from datetime import datetime, timedelta

from pydantic import Field

from .base import Command, Metadata


def generate_id() -> str:
    return str(uuid.uuid1())


def generate_secret() -> str:
    return secrets.token_urlsafe(64)


class CreateAccount(Command):
    username: str = Field(...)
    password: str = Field(...)
    email: str = Field(...)
    lang: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    metadata: Metadata = Metadata(category="user", name="create_user", schemaVersion=1)


class CreateAuthnToken(Command):
    user_id: str  # UUID
    user_agent: str
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now() + timedelta(minutes=30)
    )
    created_at: datetime = Field(default_factory=datetime.now)
    id: str = Field(default_factory=generate_id)
    token: str = Field(default_factory=generate_secret)
    metadata: Metadata = Metadata(category="user", name="authenticate", schemaVersion=1)
