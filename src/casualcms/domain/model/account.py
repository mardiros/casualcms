from dataclasses import field
from datetime import datetime
from enum import Enum

import bcrypt
from pydantic import Field
from pydantic.dataclasses import dataclass

from casualcms.domain.messages import Event

from .base import AbstractModel


class AccountStatus(Enum):
    active = "active"
    locked = "locked"


@dataclass
class Account(AbstractModel):

    id: str = field()  # UUID
    created_at: datetime = field()
    username: str = field()
    password: str = field()

    email: str = field()
    lang: str = field()

    status: AccountStatus = field(default=AccountStatus.active)
    events: list[Event] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.id)

    def __post_init__(self) -> None:
        self.password = bcrypt.hashpw(
            self.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def match_password(self, password: str) -> bool:
        encoded_pwd = self.password.encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), encoded_pwd)


@dataclass
class AuthnToken(AbstractModel):
    """Authentication tokens"""

    id: str = field()  # UUID
    token: str = field()
    account_id: str = field()  # UUID
    created_at: datetime = field()
    expires_at: datetime = field()
    client_addr: str = field()
    user_agent: str = field()

    def has_expired(self) -> bool:
        return self.expires_at < datetime.utcnow()
