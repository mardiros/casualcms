from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken


async def test_list_template(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/templates",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    # assert resp.status_code == 200
    assert resp.json() == [{"type": "tests.unittests.fixtures:RootPage"}]


async def test_list_template_for_childs(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/templates",
        params={"type": "tests.unittests.fixtures:RootPage"},
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    # assert resp.status_code == 200
    assert resp.json() == [
        {"type": "casual:CategoryPage"},
        {"type": "casual:SectionPage"},
    ]
