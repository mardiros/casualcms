import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from .base import Command, Metadata


def generate_id():
    return str(uuid.uuid1())


def generate_secret():
    return secrets.token_urlsafe(64)


@dataclass(frozen=True)
class CreateAccount(Command):
    username: str
    password: str
    email: str
    lang: str
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_id)
    metadata: Metadata = Metadata("user", "create_user", 1)


@dataclass(frozen=True)
class CreateAuthnToken(Command):
    user_id: str  # UUID
    user_agent: str
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(minutes=30)
    )
    created_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=generate_id)
    token: str = field(default_factory=generate_secret)
    metadata: Metadata = Metadata("user", "authenticate", 1)
