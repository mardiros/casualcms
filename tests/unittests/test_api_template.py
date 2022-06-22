from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken

from .fixtures import RootPage


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


async def test_show_template(client: TestClient, authntoken: AuthnToken):
    resp = client.get(
        f"/api/templates/{RootPage.__meta__.type}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    # assert resp.status_code == 200
    assert resp.json() == {
        "schema": {
            "definitions": {
                "Paragraph": {
                    "properties": {
                        "body": {
                            "title": "Body",
                            "type": "string",
                            "widget": "textarea",  # FIXME
                        },
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["body"],
                    "title": "Paragraph",
                    "type": "object",
                }
            },
            "properties": {
                "body": {
                    "title": "Body",
                    "type": "array",
                    "default": [],
                    "items": {"$ref": "#/definitions/Paragraph"},
                },
                "description": {"title": "Description", "type": "string"},
                "hero_title": {
                    "title": "Hero Title",
                    "type": "string",
                    "description": "Title of the hero section",
                },
                "id": {
                    "title": "Id",
                    "type": "string",
                    "widget": "hidden",  # FIXME
                },
                "slug": {"title": "Slug", "type": "string"},
                "title": {"title": "Title", "type": "string"},
            },
            "required": ["id", "slug", "title", "description", "hero_title"],
            "title": "RootPage",
            "type": "object",
        },
        "uiSchema": {
            "id": {"ui:widget": "hidden"},
            "slug": {"ui:widget": "text"},
            "hero_title": {"ui:widget": "text"},
            "title": {"ui:widget": "text"},
            "description": {"ui:widget": "text"},
            "body": {
                "items": {
                    "title": {"ui:widget": "text"},
                    "body": {"ui:widget": "textarea"},
                }
            },
        },
    }
