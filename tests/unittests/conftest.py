import os
from pathlib import Path
from typing import AsyncGenerator, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from casualcms.adapters.uow_inmemory import InMemoryUnitOfWork
from casualcms.config import Settings
from casualcms.domain.messages.commands import (
    CreateAccountCipheredPassword,
    CreateAuthnToken,
    CreatePage,
    CreateSite,
    CreateSnippet,
    generate_id,
)
from casualcms.domain.model import Account, AuthnToken, Page, Site
from casualcms.domain.model.snippet import Snippet
from casualcms.entrypoint import bootstrap
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.casualblog.models import HomePage


@pytest.fixture()
def app_settings() -> Iterator[Settings]:
    os.environ["casualcms_template_search_path"] = str(
        (Path(__file__).parent / "templates").resolve()
    )

    yield Settings()  # type: ignore
    del os.environ["casualcms_template_search_path"]


@pytest.fixture()
async def uow(app_settings: Settings) -> AsyncGenerator[AbstractUnitOfWork, None]:
    uow = InMemoryUnitOfWork(app_settings)
    await uow.initialize()
    yield uow
    await uow.dispose()


@pytest.fixture()
def messagebus() -> MessageRegistry:
    return MessageRegistry()


@pytest.fixture()
async def app(
    app_settings: Settings, uow: AbstractUnitOfWork, messagebus: MessageRegistry
) -> FastAPI:

    settings = Settings(unit_of_work=uow, messagebus=messagebus)  # type: ignore
    app = await bootstrap(settings)
    return app


@pytest.fixture()
async def admin_account(
    app_settings: Settings,
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Account, None]:
    async with uow as uow:
        account = await messagebus.handle(
            CreateAccountCipheredPassword(
                username=app_settings.admin_username,
                password="$2b$12$aGuSi3OWlcqJFQ/PvEoFieEB4RqEGoKzbpbyVIo6BDrdp3IWZXnBu",
                email=app_settings.admin_email,
                lang="en",
            ),
            uow,
        )
    yield account


@pytest.fixture()
async def authntoken(
    app: FastAPI,
    admin_account: Account,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[AuthnToken, None]:
    async with uow as uow:
        token = await messagebus.handle(
            CreateAuthnToken(
                account_id=admin_account.id,
                user_agent="Bot/2.0",
                client_addr="1.2.3.4",
            ),
            uow,
        )
    yield token


@pytest.fixture
async def home_page(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Page, None]:
    async with uow as uow:
        page = await messagebus.handle(
            CreatePage(
                type="blog:HomePage",
                payload={
                    "id": generate_id(),
                    "slug": "home",
                    "title": "hello world - casualcms",
                    "description": "I am so glad to be there",
                    "hero_title": "Welcome aboard!",
                },
            ),
            uow,
        )
    yield page


@pytest.fixture
async def sub_page(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
    home_page: HomePage,
) -> AsyncGenerator[Page, None]:
    async with uow as uow:
        page = await messagebus.handle(
            CreatePage(
                type="blog:CategoryPage",
                payload={
                    "id": generate_id(),
                    "parent": home_page,
                    "slug": "sub",
                    "title": "a sub page",
                    "description": "I am so glad to be a sub page",
                    "hero_title": "a sub page",
                },
            ),
            uow,
        )
    yield page


@pytest.fixture
async def header_snippet(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Snippet, None]:
    async with uow as uow:
        snippet = await messagebus.handle(
            CreateSnippet(
                type="blog:HeaderSnippet",
                slug="header",
                body={
                    "title": "A personal blog",
                    "links": [
                        {"title": "cats", "href": "/cats"},
                        {"title": "dogs", "href": "/dogs"},
                    ],
                },
            ),
            uow,
        )
    yield snippet


@pytest.fixture
async def default_site(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
    home_page: Page,
) -> AsyncGenerator[Site, None]:
    async with uow as uow:
        page = await messagebus.handle(
            CreateSite(
                hostname="www.example.net",
                default=True,
                root_page_path=home_page.path,
                secure=False,
            ),
            uow,
        )
    yield page


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)
