from typing import Any, Dict

from behave import given  # type: ignore
from blacksmith import SyncClient, SyncHTTPBearerMiddleware


@given('a "{key}" snippet of type "{snippet_type}"')
def create_snippet(context: Any, key: str, snippet_type: str) -> None:

    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    payload: Dict[str, Any] = {
        "type": snippet_type,
        "payload": {
            "key": key,
        },
    }

    if snippet_type == "blog:HeaderSnippet":
        payload = {
            "type": snippet_type,
            "payload": {
                "key": key,
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
    resp = api.snippet.post(payload)
    if resp.is_err():
        exc = resp.unwrap_err()
        print(exc.response.json)
        raise exc
