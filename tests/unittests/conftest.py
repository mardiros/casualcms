import pytest
from fastapi.testclient import TestClient

from casualcms.api.service.messagebus import MessageRegistry
from casualcms.entrypoint import app
from tests.unittests.fixtures import InMemoryUnitOfWork


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def uow():
    return InMemoryUnitOfWork()


@pytest.fixture()
def messagebus():
    return MessageRegistry()
