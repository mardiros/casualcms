from typing import Any, Mapping

import pytest
from fastapi.testclient import TestClient

from casualcms.domain.messages.commands import CreateSite
from casualcms.domain.model import AuthnToken, DraftPage, Site
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.unittests.orm.fixtures import fake_site


async def test_api_create_site_403(
    client: TestClient,
    draft_hp: DraftPage[Any],
):
    site = fake_site(draft_hp)
    resp = client.post("/api/sites", json=site.dict())
    assert resp.status_code == 403


async def test_api_create_site(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[Any],
):
    site = fake_site(draft_hp)
    resp = client.post(
        "/api/sites",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=site.dict(),
    )
    assert resp.status_code == 201
    assert resp.json() == {
        "hostname": site.hostname,
        "default": site.default,
        "secure": site.secure,
        "root_page_path": draft_hp.path,
    }


async def test_api_create_site_422(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[Any],
):
    site = fake_site(draft_hp).dict()
    site["root_page_path"] = "/not-me"
    resp = client.post(
        "/api/sites",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=site,
    )
    assert resp.status_code == 422
    assert resp.json() == {
        "detail": [{"loc": ["body", "root_page_path"], "msg": "Unknown page"}]
    }


async def test_api_list_sites_403(
    client: TestClient,
    draft_hp: DraftPage[Any],
    default_site: Site,
):
    resp = client.get("/api/sites")
    assert resp.status_code == 403


async def test_api_list_sites(
    client: TestClient,
    authntoken: AuthnToken,
    draft_hp: DraftPage[Any],
    default_site: Site,
):
    resp = client.get(
        "/api/sites",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "hostname": default_site.hostname,
            "default": True,
            "secure": False,
            "root_page_path": draft_hp.path,
        }
    ]


def test_get_site_403(
    client: TestClient,
    default_site: Site,
    draft_hp: DraftPage[Any],
):
    resp = client.get(f"/api/sites/{default_site.hostname}")
    assert resp.status_code == 403


def test_get_site(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    draft_hp: DraftPage[Any],
):
    resp = client.get(
        f"/api/sites/{default_site.hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "hostname": default_site.hostname,
        "default": True,
        "secure": False,
        "root_page_path": draft_hp.path,
    }


def test_get_site_404(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    draft_hp: DraftPage[Any],
):
    resp = client.get(
        "/api/sites/www.e404.net",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 404
    assert resp.json() == {
        "detail": [{"loc": ["path", "hostname"], "msg": "Site not found"}]
    }


async def test_update_site_403(
    client: TestClient,
    default_site: Site,
    draft_subpage: DraftPage[Any],
    uow: AbstractUnitOfWork,
):
    old_hostname = default_site.hostname
    resp = client.patch(
        f"/api/sites/{old_hostname}",
        json={
            "hostname": "new.example.net",
            "root_page_path": draft_subpage.path,
            "secure": True,
        },
    )
    assert resp.status_code == 403


async def test_update_site(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    draft_subpage: DraftPage[Any],
    uow: AbstractUnitOfWork,
):
    old_hostname = default_site.hostname
    resp = client.patch(
        f"/api/sites/{old_hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json={
            "hostname": "new.example.net",
            "root_page_path": draft_subpage.path,
            "secure": True,
        },
    )
    assert resp.status_code == 202
    assert resp.json() == {"message": "Resource Updated"}

    async with uow as uow:
        rsaved_site = await uow.sites.by_hostname("new.example.net")
    assert rsaved_site.is_ok()
    saved_site = rsaved_site.unwrap()
    assert saved_site.id == default_site.id
    assert saved_site.root_page_path == draft_subpage.path
    assert saved_site.draft_id == draft_subpage.id
    assert saved_site.secure is True

    async with uow as uow:
        old_site = await uow.sites.by_hostname(old_hostname)
    assert old_site.is_err()
    assert old_site.unwrap_err().name == "site_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "site": CreateSite(
                hostname="example1.net",
                default=False,
                secure=False,
                root_page_path="",
            ),
            "json": {
                "secure": True,
            },
            "expect_default": False,
            "expect_secure": True,
        },
        {
            "site": CreateSite(
                hostname="example2.net",
                default=False,
                secure=False,
                root_page_path="",
            ),
            "json": {
                "default": True,
            },
            "expect_default": True,
            "expect_secure": False,
        },
        {
            "site": CreateSite(
                hostname="example3.net",
                default=True,
                secure=True,
                root_page_path="",
            ),
            "json": {
                "default": False,
                "secure": False,
            },
            "expect_default": False,
            "expect_secure": False,
        },
    ],
)
async def test_update_site_flags(
    params: Mapping[str, Any],
    client: TestClient,
    authntoken: AuthnToken,
    site: Site,
    uow: AbstractUnitOfWork,
):
    old_hostname = site.hostname
    resp = client.patch(
        f"/api/sites/{old_hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
        json=params["json"],
    )
    # assert resp.status_code == 202
    assert resp.json() == {"message": "Resource Updated"}

    async with uow as uow:
        rsaved_site = await uow.sites.by_hostname(params["site"].hostname)
    assert rsaved_site.is_ok()
    saved_site = rsaved_site.unwrap()
    assert saved_site.secure is params["expect_secure"]
    assert saved_site.default is params["expect_default"]


async def test_delete_site_403(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(f"/api/sites/{default_site.hostname}")
    assert resp.status_code == 403


async def test_delete_site(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        f"/api/sites/{default_site.hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 204
    async with uow as uow:
        saved_site = await uow.sites.by_hostname(default_site.hostname)
    assert saved_site.is_err()
    assert saved_site.unwrap_err().name == "site_not_found"


async def test_delete_site_404(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    uow: AbstractUnitOfWork,
):
    resp = client.delete(
        f"/api/sites/not-{default_site.hostname}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 404
