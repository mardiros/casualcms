import os
from pathlib import Path
from typing import Any, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import casualcms.api
import casualcms.service.handlers
import casualcms.ui
from casualcms.adapters.fastapi import FastAPIConfigurator
from casualcms.adapters.uow_inmemory import InMemoryUnitOfWork
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork


@pytest.fixture
def app_settings() -> Iterator[None]:
    os.environ["casualcms_template_search_path"] = str(
        (Path(__file__).parent / "templates").resolve()
    )
    yield None
    del os.environ["casualcms_template_search_path"]


@pytest.fixture
def uow() -> Iterator[AbstractUnitOfWork]:
    uow = InMemoryUnitOfWork()
    yield uow
    uow.accounts.accounts.clear()  # type: ignore


@pytest.fixture()
def messagebus() -> MessageRegistry:
    return MessageRegistry()


@pytest.fixture
def app(uow: AbstractUnitOfWork, messagebus: MessageRegistry) -> FastAPI:
    settings: dict[str, Any] = {
        "unit_of_work": uow,
        "messagebus": messagebus,
    }
    with FastAPIConfigurator(settings) as configurator:
        configurator.scan(casualcms.api, categories=["fastapi"])
        configurator.scan(casualcms.ui, categories=["fastapi"])

        configurator.scan(casualcms.service.handlers, categories=["messagebus"])

        app = configurator.app

    return app


@pytest.fixture
def client(app: FastAPI):
    return TestClient(app)
