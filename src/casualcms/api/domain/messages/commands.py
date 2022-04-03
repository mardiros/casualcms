from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base import Command, Metadata


@dataclass(frozen=True)
class CreateAccount(Command):
    id: str
    created_at: datetime
    username: str
    password: str
    email: str
    lang: str
    phone: str
    metadata: Metadata = Metadata("user", "create_user", 1)


@dataclass(frozen=True)
class CreateAuthnToken(Command):
    id: str
    token: str
    user_id: str  # UUID
    created_at: datetime
    expires_at: Optional[datetime]
    client_addr: str
    user_agent: str
    metadata: Metadata = Metadata("user", "authenticate", 1)
