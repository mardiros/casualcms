from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.setting import Setting
from casualcms.domain.model.site import Site
from casualcms.domain.repositories.setting import SettingRepositoryResult
from casualcms.service.unit_of_work import AbstractUnitOfWork

from ..casualblog.models import ContactSetting, FeatureFlagSetting


async def test_api_create_setting_403(
    client: TestClient,
    uow: AbstractUnitOfWork,
    default_site: Site,
):
    resp = client.post(
        f"/api/settings/{default_site.hostname}",
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
    assert resp.json() == {
        "metadata": {
            "key": "ff",
            "hostname": default_site.hostname,
        },
    }
    assert resp.status_code == 201

    async with uow as uow:
        rsetting: SettingRepositoryResult = await uow.settings.by_key(
            default_site.hostname, "ff"
        )
        assert rsetting.is_ok()
        setting: Setting[FeatureFlagSetting] = rsetting.unwrap()
        # https://github.com/pydantic/pydantic/issues/6895
        assert setting.key == "ff"
        assert setting.hostname == "www.example.net"
        assert setting.setting.model_dump() == {
            "use_another_stuff": False,
            "use_stuff": True,
        }


async def test_api_list_setting_403(client: TestClient, default_site: Site):
    resp = client.get(
        f"/api/settings/{default_site.hostname}",
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
        {"metadata": {"key": "contact", "hostname": default_site.hostname}},
        {"metadata": {"key": "ff", "hostname": default_site.hostname}},
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
        "metadata": {
            "key": "ff",
            "hostname": default_site.hostname,
        }
    }

    async with uow as uow:
        rsetting: SettingRepositoryResult = await uow.settings.by_key(
            default_site.hostname, "ff"
        )
        assert rsetting.is_ok()
        setting = rsetting.unwrap()
        assert setting.setting.use_stuff is True
        assert setting.setting.use_another_stuff is True


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
        "metadata": {
            "key": "ff",
            "hostname": default_site.hostname,
        },
        "use_stuff": True,
        "use_another_stuff": False,
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
        rsetting: SettingRepositoryResult = await uow.settings.by_key(
            default_site.hostname, "ff"
        )
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
