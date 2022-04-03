import pytest
from fastapi.testclient import TestClient

from casualcms.adapters.uow_inmemory import InMemoryUnitOfWork
from casualcms.entrypoint import app
from casualcms.service.messagebus import MessageRegistry


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def uow():
    return InMemoryUnitOfWork()


@pytest.fixture()
def messagebus():
    return MessageRegistry()
