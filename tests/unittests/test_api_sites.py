
from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page
from casualcms.domain.model.site import Site
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.unittests.orm.fixtures import fake_site


async def test_api_create_site_403(
    client: TestClient,
    home_page: Page,
):
    site = fake_site(home_page)
    resp = client.post("/api/sites", json=site.dict())
    assert resp.status_code == 403


async def test_api_create_site(
    client: TestClient,
    authntoken: AuthnToken,
    home_page: Page,
):
    site = fake_site(home_page)
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
        "root_page_path": home_page.path,
    }


async def test_api_list_sites_403(
    client: TestClient,
    home_page: Page,
    default_site: Site,
):
    resp = client.get("/api/sites")
    assert resp.status_code == 403


async def test_api_list_sites(
    client: TestClient,
    authntoken: AuthnToken,
    home_page: Page,
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
            "root_page_path": home_page.path,
        }
    ]


def test_get_site_403(
    client: TestClient,
    default_site: Site,
    home_page: Page,
):
    resp = client.get(f"/api/sites/{default_site.hostname}")
    assert resp.status_code == 403


def test_get_site(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    home_page: Page,
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
        "root_page_path": home_page.path,
    }


def test_get_site_404(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    home_page: Page,
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
    sub_page: Page,
    uow: AbstractUnitOfWork,
):
    old_hostname = default_site.hostname
    resp = client.patch(
        f"/api/sites/{old_hostname}",
        json={
            "hostname": "new.example.net",
            "root_page_path": sub_page.path,
            "secure": True,
        },
    )
    assert resp.status_code == 403


async def test_update_site(
    client: TestClient,
    authntoken: AuthnToken,
    default_site: Site,
    sub_page: Page,
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
            "root_page_path": sub_page.path,
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
    assert saved_site.page_id == default_site.page_id
    assert saved_site.secure is True

    async with uow as uow:
        old_site = await uow.sites.by_hostname(old_hostname)
    assert old_site.is_err()
    assert old_site.unwrap_err().name == "site_not_found"


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
