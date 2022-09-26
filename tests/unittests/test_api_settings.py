from typing import cast

from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.site import Site
from casualcms.service.unit_of_work import AbstractUnitOfWork

from ..casualblog.models import ContactSetting, FeatureFlagSetting


async def test_api_create_setting_403(
    client: TestClient,
    uow: AbstractUnitOfWork,
    default_site: Site,
):
    resp = client.post(
        f"/api/settings/{default_site.hostname}",
        headers={},
        json={"type": "blog:FeatureFlagSetting", "payload": {}},
    )
    # XXX Fast api is raising a 403, should be a 401 to me
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_api_create_setting(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    uow: AbstractUnitOfWork,
):
    resp = client.post(
        f"/api/settings/{default_site.hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "key": "ff",
            "payload": {
                "use_stuff": True,
            },
        },
    )
    assert resp.status_code == 201
    assert resp.json() == {
        "meta": {"key": "ff"},
        "hostname": default_site.hostname,
    }
    async with uow as uow:
        setting = (await uow.settings.by_key(default_site.hostname, "ff")).unwrap()
        assert setting.__meta__.key == "ff"
        assert setting.dict() == {
            "hostname": "www.example.net",
            "use_stuff": True,
            "use_another_stuff": None,
        }


async def test_api_list_setting_403(client: TestClient, default_site: Site):
    resp = client.get(
        f"/api/settings/{default_site.hostname}",
        headers={},
    )
    # XXX Fast api is raising a 403, should be a 401 to me
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_api_list_setting(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    ff_setting: FeatureFlagSetting,
    contact_setting: ContactSetting,
):
    resp = client.get(
        f"/api/settings/{default_site.hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"meta": {"key": "contact"}, "hostname": default_site.hostname},
        {"meta": {"key": "ff"}, "hostname": default_site.hostname},
    ]


async def test_api_patch_setting_403(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    ff_setting: FeatureFlagSetting,
    uow: AbstractUnitOfWork,
):
    resp = client.patch(
        f"/api/settings/{default_site.hostname}/ff",
        json={
            "use_stuff": True,
        },
    )
    assert resp.status_code == 403


async def test_api_patch_setting(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    ff_setting: FeatureFlagSetting,
    uow: AbstractUnitOfWork,
):
    resp = client.patch(
        f"/api/settings/{default_site.hostname}/ff",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "use_stuff": True,
            "use_another_stuff": True,
        },
    )
    assert resp.status_code == 202
    assert resp.json() == {
        "meta": {"key": "ff"},
        "hostname": default_site.hostname,
    }

    async with uow as uow:
        rsetting = await uow.settings.by_key(default_site.hostname, "ff")
        assert rsetting.is_ok()
        setting = cast(FeatureFlagSetting, rsetting.unwrap())
        assert setting.use_stuff is True
        assert setting.use_another_stuff is True


async def test_api_get_setting_403(
    client: TestClient,
    default_site: Site,
    uow: AbstractUnitOfWork,
):
    resp = client.get(f"/api/settings/{default_site.hostname}/ff")
    assert resp.status_code == 403


async def test_api_get_setting(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    ff_setting: FeatureFlagSetting,
    uow: AbstractUnitOfWork,
):
    resp = client.get(
        f"/api/settings/{default_site.hostname}/ff",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "meta": {"key": "ff"},
        "hostname": default_site.hostname,
        "use_stuff": True,
        "use_another_stuff": None,
    }


async def test_api_delete_setting_403(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    ff_setting: FeatureFlagSetting,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(f"/api/settings/{default_site.hostname}/ff")
    assert resp.status_code == 403


async def test_api_delete_setting(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    ff_setting: FeatureFlagSetting,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        f"/api/settings/{default_site.hostname}/ff",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 204
    assert resp.text == ""

    async with uow as uow:
        rsetting = await uow.settings.by_key(default_site.hostname, "ff")
        assert rsetting.is_err()
        assert rsetting.unwrap_err().name == "setting_not_found"


async def test_api_delete_setting_422(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        f"/api/settings/{default_site.hostname}/e404",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [{"loc": ["querystring", "key"], "msg": "Unknown setting"}]
    }
