"""
Message base classes.

`Command` and `Event` are two types used to handle changes in the model.

"""

from dataclasses import dataclass
from typing import Optional


@dataclass()
class Metadata:
    category: str
    name: str
    schemaVersion: int
    clientAddr: Optional[str] = None
    userId: Optional[str] = None


class Message:
    """Base class for messaging."""


class Command(Message):
    """Baseclass for message of type command."""


class Event(Message):
    """Baseclass for message of type event."""
