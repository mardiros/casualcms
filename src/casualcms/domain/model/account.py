from datetime import datetime
from enum import Enum

import bcrypt
from pydantic import BaseModel, Field

from casualcms.domain.messages import Event

uuid = str


class AccountStatus(Enum):
    active = "active"
    locked = "locked"


class Account(BaseModel):

    id: uuid = Field(...)
    created_at: datetime = Field(...)
    username: str = Field(...)
    password: str = Field(...)

    email: str = Field(...)
    lang: str = Field(...)

    status: AccountStatus = Field(default=AccountStatus.active)
    events: list[Event] = Field(default_factory=list, exclude=True)

    def __hash__(self) -> int:
        return hash(self.id)  # type: ignore

    def match_password(self, password: str) -> bool:
        encoded_pwd = self.password.encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), encoded_pwd)


class AuthnToken(BaseModel):
    """Authentication tokens"""

    id: uuid = Field(...)
    token: str = Field(...)
    user_id: uuid = Field(...)
    created_at: datetime = Field(...)
    expires_at: datetime = Field(...)
    client_addr: str = Field(...)
    user_agent: str = Field(...)

    def has_expired(self) -> bool:
        return self.expires_at < datetime.utcnow()
