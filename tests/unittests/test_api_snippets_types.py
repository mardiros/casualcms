from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken


async def test_list_types_403(client: TestClient):

    resp = client.get("/api/snippets-types")
    assert resp.status_code == 403


async def test_list_types(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/snippets-types",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == [
        {
            "title": "Header Snippet",
            "type": "blog:HeaderSnippet",
        },
        {
            "title": "Related Post Snippet",
            "type": "blog:RelatedPostSnippet",
        },
        {
            "title": "Snippet Block",
            "type": "blog:SnippetBlock",
        },
        {
            "title": "Footer Snippet",
            "type": "tests.casualblog.models:FooterSnippet",
        },
    ]


async def test_get_type_403(client: TestClient):

    resp = client.get("/api/snippets-types/blog:HeaderSnippet")
    assert resp.status_code == 403


async def test_get_type(client: TestClient, authntoken: AuthnToken):

    resp = client.get(
        "/api/snippets-types/blog:HeaderSnippet",
        headers={
            "Authorization": f"Bearer {authntoken.token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        "schema": {
            "$defs": {
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
                    "items": {"$ref": "#/$defs/Link"},
                    "title": "Links",
                    "type": "array",
                },
                "key": {"pattern": "^[^/]+$", "title": "Key", "type": "string"},
                "title": {"title": "Title", "type": "string"},
            },
            "required": ["key", "title"],
            "title": "Header Snippet",
            "type": "object",
        },
        "uiSchema": {
            "links": {
                "items": {
                    "href": {"ui:placeholder": "href", "ui:widget": "text"},
                    "title": {"ui:placeholder": "title", "ui:widget": "text"},
                }
            },
            "key": {"ui:placeholder": "key", "ui:widget": "text"},
            "title": {"ui:placeholder": "title", "ui:widget": "text"},
        },
    }
