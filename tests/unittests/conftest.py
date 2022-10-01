import os
from pathlib import Path
from typing import Any, AsyncGenerator, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from casualcms.adapters.fastapi import FastAPIConfigurator
from casualcms.adapters.uow_inmemory import InMemoryUnitOfWork
from casualcms.config import Settings
from casualcms.domain.messages.commands import (
    CreateAccount,
    CreateAccountCipheredPassword,
    CreateAuthnToken,
    CreatePage,
    CreateSetting,
    CreateSite,
    CreateSnippet,
    PublishPage,
    generate_id,
)
from casualcms.domain.model import (
    Account,
    AuthnToken,
    DraftPage,
    PublishedPage,
    Setting,
    Site,
    Snippet,
)
from casualcms.domain.repositories.page import PageRepositoryResult
from casualcms.entrypoint import bootstrap
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.casualblog.models import CategoryPage, HomePage


@pytest.fixture()
def app_settings() -> Iterator[Settings]:
    os.environ["casualcms_template_search_path"] = str(
        (Path(__file__).parent / "templates").resolve()
    )
    os.environ["casualcms_assets_path"] = str(
        (Path(__file__).parent / "assets").resolve()
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


class ConfiguredOnce:
    app: FastAPI | None = None


@pytest.fixture()
async def app(
    app_settings: Settings, uow: AbstractUnitOfWork, messagebus: MessageRegistry
) -> FastAPI:

    settings = Settings(unit_of_work=uow, messagebus=messagebus)  # type: ignore
    if ConfiguredOnce.app:
        with FastAPIConfigurator(settings) as configurator:
            await configurator.initialize()
            configurator.app = ConfiguredOnce.app
            import casualcms.service.handlers

            configurator.scan(casualcms.service.handlers, categories=["messagebus"])
        app = ConfiguredOnce.app
    else:
        app = await bootstrap(settings)
        ConfiguredOnce.app = app
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
    yield account.unwrap()


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
                user_id=admin_account.id,
                user_agent="Bot/2.0",
                client_addr="1.2.3.4",
            ),
            uow,
        )
    yield token.unwrap()


@pytest.fixture
async def draft_hp(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[DraftPage[HomePage], None]:
    async with uow as uow:
        page_id = generate_id()
        await messagebus.handle(
            CreatePage(
                id=page_id,
                type="blog:HomePage",
                payload={
                    "slug": "home",
                    "title": "hello world - casualcms",
                    "description": "I am so glad to be there",
                    "hero_title": "Welcome aboard!",
                },
            ),
            uow,
        )
        page = await uow.drafts.by_id(page_id)  # type: ignore
        yield page.unwrap()


@pytest.fixture
async def draft_subpage(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
    draft_hp: DraftPage[HomePage],
) -> AsyncGenerator[DraftPage[CategoryPage], None]:
    async with uow as uow:
        page_id = generate_id()
        await messagebus.handle(
            CreatePage(
                id=page_id,
                type="blog:CategoryPage",
                payload={
                    "parent": draft_hp.page,
                    "slug": "sub",
                    "title": "a sub page",
                    "description": "I am so glad to be a sub page",
                    "hero_title": "a sub page",
                },
            ),
            uow,
        )
        page = await uow.drafts.by_id(page_id)  # type: ignore  # type:ignore
        yield page.unwrap()


@pytest.fixture
async def header_snippet(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Snippet[Any], None]:
    async with uow as uow:
        snippet = await messagebus.handle(
            CreateSnippet(
                type="blog:HeaderSnippet",
                key="header",  # type: ignore
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
    yield snippet.unwrap()


@pytest.fixture
async def alt_header_snippet(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Snippet[Any], None]:
    async with uow as uow:
        snippet = await messagebus.handle(
            CreateSnippet(
                type="blog:HeaderSnippet",
                key="alt-header",  # type: ignore
                body={
                    "title": "Alternative title",
                    "links": [
                        {"title": "cats", "href": "/cats"},
                        {"title": "dogs", "href": "/dogs"},
                    ],
                },
            ),
            uow,
        )
    yield snippet.unwrap()


@pytest.fixture
async def footer_snippet(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Snippet[Any], None]:
    async with uow as uow:
        snippet = await messagebus.handle(
            CreateSnippet(
                type="tests.casualblog.models:FooterSnippet",
                key="footer",  # type: ignore
                body={
                    "links": [
                        {"title": "about", "href": "/about"},
                    ],
                },
            ),
            uow,
        )
    yield snippet.unwrap()


@pytest.fixture
async def default_site(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
    draft_hp: DraftPage[HomePage],
) -> AsyncGenerator[Site, None]:
    async with uow as uow:
        site = await messagebus.handle(
            CreateSite(
                hostname="www.example.net",
                default=True,
                root_page_path=draft_hp.path,
                secure=False,
            ),
            uow,
        )
    yield site.unwrap()


@pytest.fixture
async def home_page(
    app: FastAPI,
    draft_hp: PublishedPage[HomePage],
    default_site: Site,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[PublishedPage[HomePage], None]:

    async with uow as uow:
        await messagebus.handle(
            PublishPage(id=draft_hp.id, site_id=default_site.id),
            uow,
        )
        ppage: PageRepositoryResult[HomePage] = await uow.pages.by_draft_page_and_site(
            draft_hp.id, default_site.id
        )
        yield ppage.unwrap()


@pytest.fixture
async def ff_setting(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    default_site: Site,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Setting, None]:
    async with uow as uow:
        setting = await messagebus.handle(
            CreateSetting(
                key="ff",
                hostname=default_site.hostname,
                body={
                    "use_stuff": True,
                },
            ),
            uow,
        )
    yield setting.unwrap()


@pytest.fixture
async def contact_setting(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    default_site: Site,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Setting, None]:
    async with uow as uow:
        setting = await messagebus.handle(
            CreateSetting(
                key="contact",
                hostname=default_site.hostname,
                body={
                    "email": "email@example.net",
                },
            ),
            uow,
        )
    yield setting.unwrap()


@pytest.fixture
async def bob_account(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Account, None]:
    bob = CreateAccount(
        username="bob",
        password="secret",
        email="bob@email.net",
        lang="en",
    )
    async with uow as uow:
        account = await messagebus.handle(bob, uow)
    yield account.unwrap()


@pytest.fixture
async def alice_account(
    app: FastAPI,
    uow: AbstractUnitOfWork,
    messagebus: MessageRegistry,
) -> AsyncGenerator[Account, None]:
    alice = CreateAccount(
        username="alice",
        password="othersecret",
        email="alice@email.net",
        lang="en",
    )
    async with uow as uow:
        account = await messagebus.handle(alice, uow)
    yield account.unwrap()


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)
