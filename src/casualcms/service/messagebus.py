"""
Propagate commands and events to every registered handles.

"""

import inspect
import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine, Dict, List, Type, TypeVar, Union, cast

import venusian  # type: ignore

from casualcms.domain.messages.base import Command, Event, Message

from .unit_of_work import AbstractUnitOfWork

log = logging.getLogger(__name__)

TCommand = TypeVar("TCommand", bound=Command)
TEvent = TypeVar("TEvent", bound=Event)

CommandHandler = Callable[[TCommand, AbstractUnitOfWork], Coroutine[Any, Any, Any]]
EventHandler = Callable[[TEvent, AbstractUnitOfWork], Coroutine[Any, Any, None]]
MessageHandler = Union[CommandHandler[TCommand], EventHandler[TEvent]]


class ConfigurationError(RuntimeError):
    """Prevents bad usage of the add_listener."""


def listen(
    wrapped: Callable[[TCommand, AbstractUnitOfWork], Coroutine[None, None, Any]]
) -> Callable[[TCommand, AbstractUnitOfWork], Coroutine[None, None, Any]]:
    """
    Decorator to listen for a message.
    """

    def callback(
        scanner: venusian.Scanner,
        name: str,
        ob: Callable[[TCommand, AbstractUnitOfWork], Coroutine[None, None, Any]],
    ) -> None:
        if not hasattr(scanner, "messagebus"):
            return  # coverage: ignore
        argsspec = inspect.getfullargspec(ob)
        msg_type = argsspec.annotations[argsspec.args[0]]
        log.info(
            "Attaching %s for %s",
            wrapped.__name__,
            msg_type,
        )
        scanner.messagebus.add_listener(msg_type, wrapped)  # type: ignore

    venusian.attach(wrapped, callback, category="messagebus")
    return wrapped


class MessageRegistry:
    """Store all the handlers for commands an events."""

    def __init__(self) -> None:
        self.commands_registry: Dict[Type[Command], CommandHandler[Command]] = {}
        self.events_registry: Dict[
            Type[Event], List[EventHandler[Event]]
        ] = defaultdict(list)

    def add_listener(
        self, msg_type: Type[Message], callback: MessageHandler[Any, Any]
    ) -> None:
        if issubclass(msg_type, Command):
            if msg_type in self.commands_registry:
                raise ConfigurationError(
                    f"{msg_type} command has been registered twice"
                )
            self.commands_registry[msg_type] = cast(CommandHandler[Command], callback)
        elif issubclass(msg_type, Event):
            self.events_registry[msg_type].append(cast(EventHandler[Event], callback))
        else:
            raise ConfigurationError(
                f"Invalid usage of the listen decorator: "
                f"type {msg_type} should be a command or an event"
            )

    def remove_listener(
        self, msg_type: type, callback: MessageHandler[Any, Any]
    ) -> None:
        if issubclass(msg_type, Command):
            if msg_type not in self.commands_registry:
                raise ConfigurationError(f"{msg_type} command has not been registered")
            del self.commands_registry[msg_type]
        elif issubclass(msg_type, Event):
            try:
                self.events_registry[msg_type].remove(
                    cast(EventHandler[Event], callback)
                )
            except ValueError:
                raise ConfigurationError(f"{msg_type} event has not been registered")
        else:
            raise ConfigurationError(
                f"Invalid usage of the listen decorator: "
                f"type {msg_type} should be a command or an event"
            )

    async def handle(self, message: Message, uow: AbstractUnitOfWork) -> Any:
        """
        Notify listener of that event registered with `messagebus.add_listener`.
        Return the first event from the command.
        """
        queue = [message]
        idx = 0
        ret = None
        while queue:
            message = queue.pop(0)
            if not isinstance(message, (Command, Event)):
                raise RuntimeError(f"{message} was not an Event or Command")
            msg_type = type(message)
            if msg_type in self.commands_registry:
                cmdret = await self.commands_registry[cast(Type[Command], msg_type)](
                    cast(Command, message), uow
                )
                if idx == 0:
                    ret = cmdret
                queue.extend(uow.collect_new_events())
            elif msg_type in self.events_registry:
                for callback in self.events_registry[cast(Type[Event], msg_type)]:
                    await callback(cast(Event, message), uow)
                    queue.extend(uow.collect_new_events())
            idx += 1
        return ret
