"""Unit of work"""
from __future__ import annotations

import abc
from types import TracebackType
from typing import Iterable, Optional, Type

from casualcms.api.domain.messages import Event
from casualcms.api.domain.repositories import AbstractAccountRepository


class AbstractUnitOfWork(abc.ABC):
    accounts: AbstractAccountRepository

    def collect_new_events(self) -> Iterable[Event]:
        for account in self.accounts.seen:
            while account.events:
                yield account.events.pop(0)

    async def initialize(self) -> None:
        """Override to initialize  repositories."""

    async def __aenter__(self) -> AbstractUnitOfWork:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        """Rollback in case of exception."""
        if exc:
            await self.rollback()

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the transation."""

    @abc.abstractmethod
    async def rollback(self) -> None:
        """Rollback the transation."""
