from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken


async def test_list_types(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/snippets-types",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {"type": "blog:HeaderSnippet"},
        {"type": "tests.casualblog.models:FooterSnippet"},
    ]


async def test_get_type(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/snippets-types/blog:HeaderSnippet",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    # assert resp.status_code == 200
    assert resp.json() == {
        "schema": {
            "definitions": {
                "Link": {
                    "properties": {
                        "href": {"title": "Href", "type": "string"},
                        "title": {"title": "Title", "type": "string"},
                    },
                    "required": ["title", "href"],
                    "title": "Link",
                    "type": "object",
                },
            },
            "properties": {
                "links": {
                    "items": {"$ref": "#/definitions/Link"},
                    "title": "Links",
                    "type": "array",
                },
                "slug": {"title": "Slug", "type": "string"},
                "title": {"title": "Title", "type": "string"},
            },
            "required": ["slug", "title"],
            "title": "HeaderSnippet",
            "type": "object",
        },
        "uiSchema": {
            "links": {
                "items": {
                    "href": {"ui:placeholder": "href", "ui:widget": "text"},
                    "title": {"ui:placeholder": "title", "ui:widget": "text"},
                }
            },
            "slug": {"ui:placeholder": "slug", "ui:widget": "text"},
            "title": {"ui:placeholder": "title", "ui:widget": "text"},
        },
    }
