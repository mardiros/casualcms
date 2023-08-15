from fastapi.testclient import TestClient

from casualcms.domain.model.account import AuthnToken

from ..casualblog.models import HomePage


async def test_list_page_types_403(client: TestClient, authntoken: AuthnToken):

    resp = client.get("/api/pages-types")
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
        {"title": "Category Page", "type": "blog:CategoryPage"},
        {"title": "Section Page", "type": "blog:SectionPage"},
        {"title": "Snippet Block Page", "type": "blog:SnippetBlockPage"},
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
            "$defs": {
                "CodeBlock": {
                    "properties": {
                        "code": {
                            "title": "Code",
                            "type": "string",
                            "widget": "textarea",
                        },
                        "language": {
                            "enum": [
                                "Bash",
                                "Go",
                                "Java",
                                "JavaScript",
                                "Python",
                                "Ruby",
                                "Rust",
                                "SQL",
                                "Typescript",
                            ],
                            "title": "Language",
                            "type": "string",
                            "widget": "select",
                        },
                    },
                    "required": ["language", "code"],
                    "title": "Code Block",
                    "description": "Code block to render code with pygment",
                    "type": "object",
                },
                "ParagraphBlock": {
                    "properties": {
                        "body": {
                            "features": ["bold", "italic", "h5"],
                            "title": "Body",
                            "type": "string",
                            "widget": "richtext",
                        },
                        "title": {"title": "Title", "type": "string", "default": ""},
                    },
                    "required": ["body"],
                    "title": "Paragraph Block",
                    "type": "object",
                },
            },
            "properties": {
                "body": {
                    "default": [],
                    "items": {
                        "anyOf": [
                            {"$ref": "#/$defs/ParagraphBlock"},
                            {"$ref": "#/$defs/CodeBlock"},
                        ]
                    },
                    "title": "Body",
                    "type": "array",
                },
                "description": {"title": "Description", "type": "string"},
                "hero_title": {
                    "description": "Title of the hero " "section",
                    "title": "Hero Title",
                    "type": "string",
                },
                "slug": {"pattern": "^[^/]+$", "title": "Slug", "type": "string"},
                "title": {"title": "Title", "type": "string"},
            },
            "required": ["slug", "title", "description", "hero_title"],
            "title": "🏠 Home Page",
            "type": "object",
        },
        "uiSchema": {
            "body": {
                "items": {
                    "body": {
                        "ui:options": {"features": ["bold", "italic", "h5"]},
                        "ui:placeholder": "body",
                        "ui:widget": "richtext",
                    },
                    "code": {"ui:placeholder": "code", "ui:widget": "textarea"},
                    "language": {"ui:placeholder": "language", "ui:widget": "select"},
                    "title": {"ui:placeholder": "title", "ui:widget": "text"},
                }
            },
            "description": {"ui:placeholder": "description", "ui:widget": "text"},
            "hero_title": {"ui:placeholder": "hero_title", "ui:widget": "text"},
            "slug": {"ui:placeholder": "slug", "ui:widget": "text"},
            "title": {"ui:placeholder": "title", "ui:widget": "text"},
        },
    }
