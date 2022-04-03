from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import bcrypt

from casualcms.domain.messages import Event


class AbstractModel:
    """Type Marker for domain model class."""


class AccountStatus(Enum):
    active = "active"
    locked = "locked"


@dataclass
class Account(AbstractModel):

    id: str  # UUID
    created_at: datetime
    username: str
    password: str

    email: str
    lang: str

    status: AccountStatus = AccountStatus.active
    events: list[Event] = field(default_factory=list)

    def __hash__(self) -> int:
        return hash(self.id)

    def __post_init__(self):
        self.password = bcrypt.hashpw(
            self.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def match_password(self, password: str) -> bool:
        encoded_pwd = self.password.encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), encoded_pwd)


@dataclass
class AuthnToken(AbstractModel):
    """Authentication tokens"""

    id: str  # UUID
    token: str
    account_id: str  # UUID
    created_at: datetime
    expires_at: datetime
    client_addr: str
    user_agent: str

    def has_expired(self):
        return self.expires_at < datetime.utcnow()
