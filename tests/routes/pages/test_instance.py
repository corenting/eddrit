from starlette.testclient import TestClient

from eddrit import __version__


def test_version(test_client: TestClient) -> None:
    response = test_client.get("/meta/version")

    assert response.status_code == 200
    assert "version" in response.json()
    assert response.json()["version"] == __version__
