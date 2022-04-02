from fastapi.testclient import TestClient


def test_api_authenticate(client: TestClient):
    resp = client.post("/api/authntokens", json={"username": "bob", "password": "bob"})
    assert resp.status_code == 401
    assert resp.json() == {
        "detail": [{"loc": ["body", "username"], "msg": "Invalid username or password"}]
    }
