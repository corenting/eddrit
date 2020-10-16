from starlette.testclient import TestClient


def test_no_referrer_middleware(test_client: TestClient) -> None:
    endpoint_res = test_client.get("/instance/version")

    assert endpoint_res.headers["Referrer-Policy"] == "no-referrer"
