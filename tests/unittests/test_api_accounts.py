from fastapi.testclient import TestClient

from casualcms.domain.messages.commands import CreateAccount
from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork


def test_api_authenticate_failed(client: TestClient):
    resp = client.post("/api/authntokens", json={"username": "bob", "password": "bob"})
    assert resp.status_code == 401
    assert resp.json() == {
        "detail": [{"loc": ["body", "username"], "msg": "Invalid username or password"}]
    }


async def test_api_authenticate_success(
    client: TestClient, messagebus: MessageRegistry, uow: AbstractUnitOfWork
):
    bob = CreateAccount(
        username="bob",
        password="secret",
        email="bob@email.net",
        lang="en",
    )
    async with uow as uow:
        await messagebus.handle(
            bob,
            uow,
        )
        await messagebus.handle(
            CreateAccount(
                username="alice",
                password="othersecret",
                email="alice@email.net",
                lang="en",
            ),
            uow,
        )

    resp = client.post(
        "/api/authntokens", json={"username": "bob", "password": "secret"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert resp.json() == {
        "expires_at": data["expires_at"],
        "lang": "en",
        "token": data["token"],
        "user_id": bob.id,
        "username": "bob",
    }

    resp = client.post(
        "/api/authntokens", json={"username": "bob", "password": "othersecret"}
    )
    assert resp.status_code == 401
