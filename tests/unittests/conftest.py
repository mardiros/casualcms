import os
from pathlib import Path
from typing import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from casualcms.adapters.uow_inmemory import InMemoryUnitOfWork
from casualcms.config import Settings
from casualcms.domain.messages.commands import CreateAuthnToken
from casualcms.entrypoint import bootstrap
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork


@pytest.fixture()
def app_settings() -> Iterator[Settings]:
    os.environ["casualcms_template_search_path"] = str(
        (Path(__file__).parent / "templates").resolve()
    )
    os.environ["casualcms_admin_password"] = "supersecret"
    yield Settings()  # type: ignore
    del os.environ["casualcms_template_search_path"]


@pytest.fixture()
def uow() -> Iterator[AbstractUnitOfWork]:
    uow = InMemoryUnitOfWork()
    yield uow
    uow.accounts.accounts.clear()  # type: ignore


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
):
    async with uow as uow:
        account = (await uow.accounts.by_username(app_settings.admin_username)).unwrap()
        yield account


@pytest.fixture()
async def authntoken(
    app_settings: Settings, uow: AbstractUnitOfWork, messagebus: MessageRegistry
):
    async with uow as uow:
        account = (await uow.accounts.by_username(app_settings.admin_username)).unwrap()
        token = await messagebus.handle(
            CreateAuthnToken(
                account_id=account.id,
                user_agent="Bot/2.0",
                client_addr="1.2.3.4",
            ),
            uow,
        )
    yield token


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)
