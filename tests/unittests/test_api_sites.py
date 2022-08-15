from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken
from casualcms.domain.model.page import Page
from casualcms.domain.model.site import Site
from casualcms.service.unit_of_work import AbstractUnitOfWork
from tests.unittests.orm.fixtures import fake_site


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
    assert resp.status_code == 200
    assert resp.json() == {
        "hostname": site.hostname,
        "default": site.default,
        "secure": site.secure,
        "root_page_path": home_page.path,
    }


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
