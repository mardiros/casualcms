import abc
import enum
from typing import TypeVar

from result import Result

from casualcms.api.domain.messages import Message

T = TypeVar("T")
E = TypeVar("E", bound=enum.Enum)
RepositoryResult = Result[T, E]


class AbstractRepository(abc.ABC):
    messages: list[Message]
