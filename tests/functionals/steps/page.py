from typing import Any, Dict

from faker import Faker
from behave import given  # type: ignore
from blacksmith import HTTPError, SyncHTTPBearerMiddleware, SyncClient

fake = Faker()


@given('a "{path}" page of type "{page_type}"')
def create_page(context: Any, path: str, page_type: str) -> None:

    path_split = path.strip("/").split("/")
    slug = path_split.pop()
    parent_path = f"/{'/'.join(path_split)}" if path_split else None
    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any, Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    payload: Dict[str, Any] = {
        "type": page_type,
        "parent": parent_path,
        "payload": {
            "id": str(fake.uuid4()),
            "slug": slug,
        },
    }

    if page_type == "blog:HomePage":
        payload = {
            "type": "blog:HomePage",
            # "parent": parent_path,
            "payload": {
                "id": str(fake.uuid4()),
                "slug": slug,
                "body": [
                    {
                        "title": fake.name(),
                        "body": f"<p>{fake.paragraph(nb_sentences=1)}</p>",
                    },
                    {
                        "title": fake.name(),
                        "body": f"<p>{fake.paragraph(nb_sentences=1)}</p>",
                    },
                ],
                "title": "welcome home",
                "hero_title": "welcome home bro!",
                "description": "there is not place like home",
            },
        }

    elif page_type == "blog:CategoryPage":
        payload = {
            "type": "blog:CategoryPage",
            "parent": parent_path,
            "payload": {
                "id": str(fake.uuid4()),
                "intro": {"title": fake.name(), "body": fake.paragraph(nb_sentences=1)},
                "slug": slug,
                "title": fake.name(),
                "description": fake.paragraph(nb_sentences=1),
                "hero_title": fake.name(),
            },
        }

    elif page_type == "blog:BlogPage":
        payload = {
            "type": "blog:BlogPage",
            "parent": parent_path,
            "payload": {
                "id": str(fake.uuid4()),
                "slug": slug,
                "title": fake.name(),
                "description": fake.paragraph(nb_sentences=1),
                "hero_title": fake.name(),
                "body": [],
            },
        }

    print(payload)
    try:
        api.page.post(payload)
    except HTTPError as exc:
        print(exc.response.json)
        raise
