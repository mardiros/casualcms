from typing import Any, List
from enum import Enum
from datetime import datetime

import bcrypt
from pydantic import BaseModel, Field


class AbstractModel(BaseModel):
    """Type Marker for domain model class."""

    id: str  # UUID
    created_at: datetime


class AccountStatus(Enum):
    active = "active"
    locked = "locked"


class Account(AbstractModel):

    id: str  # UUID
    created_at: datetime
    username: str
    password: str

    email: str
    lang: str

    status: AccountStatus = AccountStatus.active
    events: List[Any] = Field(default_factory=list)

    def __init__(self, **data: Any):
        data["password"] = bcrypt.hashpw(
            data["password"].encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        super().__init__(**data)

    def match_password(self, password: str) -> bool:
        encoded_pwd = self.password.encode("utf-8")
        return bcrypt.checkpw(password.encode("utf-8"), encoded_pwd)
