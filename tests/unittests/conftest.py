from fastapi.testclient import TestClient
import pytest
from casualcms.entrypoint import app


@pytest.fixture
def client():
    return TestClient(app)
