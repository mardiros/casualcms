from fastapi.testclient import TestClient

from casualcms.domain.model.account import Account, AuthnToken
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork


def test_api_authenticate_failed(client: TestClient):
    resp = client.post("/api/authntokens", json={"username": "bob", "password": "bob"})
    assert resp.status_code == 401
    assert resp.json() == {
        "detail": [{"loc": ["body", "username"], "msg": "Invalid username or password"}]
    }


async def test_api_authenticate_success(
    client: TestClient,
    messagebus: MessageRegistry,
    bob_account: Account,
    alice_account: Account,
    uow: AbstractUnitOfWork,
):
    resp = client.post(
        "/api/authntokens", json={"username": "bob", "password": "secret"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert resp.json() == {
        "expires_at": data["expires_at"],
        "lang": "en",
        "token": data["token"],
        "user_id": bob_account.id,
        "username": "bob",
    }

    resp = client.post(
        "/api/authntokens", json={"username": "bob", "password": "othersecret"}
    )
    assert resp.status_code == 401


def test_api_logout(
    client: TestClient,
    authntoken: AuthnToken,
    uow: AbstractUnitOfWork,
):
    assert authntoken.token in uow.authn_tokens.tokens  # type: ignore
    resp = client.delete(
        "/api/authntokens",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 204
    assert resp.text == ""
    assert authntoken.token not in uow.authn_tokens.tokens  # type: ignore
