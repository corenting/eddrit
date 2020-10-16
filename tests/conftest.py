import pytest
from starlette.testclient import TestClient

from eddrit.app import app


@pytest.fixture(scope="session")
def test_client() -> TestClient:
    return TestClient(app)
