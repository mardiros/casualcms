import abc
import enum
from types import EllipsisType
from typing import TypeVar

from result import Result

from casualcms.domain.messages import Message

T = TypeVar("T")
E = TypeVar("E", bound=enum.Enum)
RepositoryResult = Result[T, E]
OperationResult = RepositoryResult[EllipsisType, E]


class AbstractRepository(abc.ABC):
    messages: list[Message]
