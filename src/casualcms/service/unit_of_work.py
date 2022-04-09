"""Unit of work"""
from __future__ import annotations

import abc
from types import TracebackType
from typing import Iterable, Optional, Type

from casualcms.domain.messages import Event
from casualcms.domain.repositories import AbstractAccountRepository
from casualcms.domain.repositories.page import AbstractPageRepository


class AbstractUnitOfWork(abc.ABC):
    accounts: AbstractAccountRepository
    pages: AbstractPageRepository

    def collect_new_events(self) -> Iterable[Event]:
        for account in self.accounts.seen:
            while account.events:
                yield account.events.pop(0)

        for page in self.pages.seen:
            while page.events:
                yield page.events.pop(0)

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