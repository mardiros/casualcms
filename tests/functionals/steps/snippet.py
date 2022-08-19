from typing import Any, Dict

from behave import given  # type: ignore
from blacksmith import HTTPError, SyncClient, SyncHTTPBearerMiddleware


@given('a "{slug}" snippet of type "{snippet_type}"')
def create_snippet(context: Any, slug: str, snippet_type: str) -> None:

    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any, Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    payload: Dict[str, Any] = {
        "type": snippet_type,
        "payload": {
            "slug": slug,
        },
    }

    if snippet_type == "blog:HeaderSnippet":
        payload = {
            "type": snippet_type,
            "payload": {
                "slug": slug,
                "title": "Casual Blog",
                "links": [
                    {
                        "title": "Cat",
                        "href": "/home/cat",
                    },
                    {
                        "title": "Dog",
                        "href": "/home/dog",
                    },
                ],
            },
        }

    print(payload)
    try:
        api.snippet.post(payload)
    except HTTPError as exc:
        print(exc.response.json)
        raise
