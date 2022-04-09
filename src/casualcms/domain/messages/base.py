"""
Message base classes.

`Command` and `Event` are two types used to handle changes in the model.

"""

from typing import Optional

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    category: str = Field(...)
    name: str = Field(...)
    schemaVersion: int = Field(...)
    clientAddr: Optional[str] = None
    userId: Optional[str] = None


class Message(BaseModel):
    """Base class for messaging."""


class Command(Message):
    """Baseclass for message of type command."""


class Event(Message):
    """Baseclass for message of type event."""
