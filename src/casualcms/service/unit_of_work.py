"""Unit of work"""
from __future__ import annotations

import abc
from types import TracebackType
from typing import TYPE_CHECKING, Iterable, Optional, Type

from casualcms.domain.repositories.setting import AbstractSettingRepository
from casualcms.domain.repositories.site import AbstractSiteRepository

if TYPE_CHECKING:  # avoid circular dependency
    from casualcms.config import Settings  # coverage: ignore

from casualcms.domain.messages import Event
from casualcms.domain.repositories import (
    AbstractAccountRepository,
    AbstractAuthnRepository,
    AbstractDraftRepository,
    AbstractSnippetRepository,
)


class AbstractUnitOfWork(abc.ABC):
    accounts: AbstractAccountRepository
    drafts: AbstractDraftRepository
    snippets: AbstractSnippetRepository
    authn_tokens: AbstractAuthnRepository
    sites: AbstractSiteRepository
    settings: AbstractSettingRepository

    @abc.abstractmethod
    def __init__(self, settings: "Settings") -> None:
        """Create the unit of work, from the given configuration"""

    def collect_new_events(self) -> Iterable[Event]:
        for account in self.accounts.seen:
            while account.events:
                yield account.events.pop(0)

        for page in self.drafts.seen:
            while page.events:
                yield page.events.pop(0)

        for site in self.sites.seen:
            while site.events:
                yield site.events.pop(0)

        for snippet in self.snippets.seen:
            while snippet.events:
                yield snippet.events.pop(0)

    async def initialize(self) -> None:
        """Override to initialize repositories."""

    async def dispose(self) -> None:
        """Override to dispose repositories."""

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
