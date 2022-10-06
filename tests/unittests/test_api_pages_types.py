from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken

from ..casualblog.models import HomePage


async def test_list_page_types_403(client: TestClient, authntoken: AuthnToken):

    resp = client.get("/api/pages-types", headers={})
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_list_page_types(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/pages-types",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"title": "🏠 Home Page", "type": "blog:HomePage"},
    ]


async def test_list_page_types_for_childs(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/pages-types",
        params={"type": "blog:HomePage"},
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"title": "blog: Category Page", "type": "blog:CategoryPage"},
        {"title": "blog: Section Page", "type": "blog:SectionPage"},
    ]


async def test_show_template_403(client: TestClient, authntoken: AuthnToken):
    resp = client.get(f"/api/pages-types/{HomePage.__meta__.type}")
    assert resp.status_code == 403
    assert resp.json() == {"detail": "Not authenticated"}


async def test_show_template(client: TestClient, authntoken: AuthnToken):
    resp = client.get(
        f"/api/pages-types/{HomePage.__meta__.type}",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
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
                "slug": {
                    "title": "Slug",
                    "type": "string",
                    "pattern": "^[^/]+$",
                },
                "title": {"title": "Title", "type": "string"},
            },
            "required": ["slug", "title", "description", "hero_title"],
            "title": "🏠 Home Page",
            "type": "object",
        },
        "uiSchema": {
            "slug": {"ui:placeholder": "slug", "ui:widget": "text"},
            "hero_title": {"ui:widget": "text", "ui:placeholder": "hero_title"},
            "title": {"ui:widget": "text", "ui:placeholder": "title"},
            "description": {"ui:widget": "text", "ui:placeholder": "description"},
            "body": {
                "items": {
                    "title": {"ui:widget": "text", "ui:placeholder": "title"},
                    "body": {"ui:widget": "textarea", "ui:placeholder": "body"},
                }
            },
        },
    }
