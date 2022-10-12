from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken


async def test_list_types_403(client: TestClient):

    resp = client.get("/api/settings-types")
    assert resp.status_code == 403


async def test_list_types(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/settings-types",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"key": "contact", "title": "Contact Setting"},
        {"key": "ff", "title": "Feature Flag"},
    ]


async def test_get_type_403(client: TestClient):

    resp = client.get("/api/settings-types/ff")
    assert resp.status_code == 403


async def test_get_type(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/settings-types/ff",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "schema": {
            "properties": {
                "use_another_stuff": {"title": "Use Another Stuff", "type": "boolean"},
                "use_stuff": {
                    "title": "Use Stuff",
                    "type": "boolean",
                    "default": False,
                },
            },
            "title": "Feature Flag",
            "type": "object",
        },
        "uiSchema": {
            "use_another_stuff": {
                "ui:placeholder": "use_another_stuff",
                "ui:widget": "checkbox",
            },
            "use_stuff": {"ui:placeholder": "use_stuff", "ui:widget": "checkbox"},
        },
    }
