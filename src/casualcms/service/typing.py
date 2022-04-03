"""
Propagate commands and events to every registered handles.

"""
import logging
from typing import Any, Callable, Coroutine, TypeVar, Union

from casualcms.domain.messages.base import Command, Event

from .unit_of_work import AbstractUnitOfWork

log = logging.getLogger(__name__)

TCommand = TypeVar("TCommand", bound=Command)
TEvent = TypeVar("TEvent", bound=Event)

CommandHandler = Callable[[TCommand, AbstractUnitOfWork], Coroutine[Any, Any, Any]]
EventHandler = Callable[[TEvent, AbstractUnitOfWork], Coroutine[Any, Any, None]]
MessageHandler = Union[CommandHandler[TCommand], EventHandler[TEvent]]
