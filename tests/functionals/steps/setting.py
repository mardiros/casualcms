from typing import Any, Dict

from behave import given  # type: ignore
from blacksmith import HTTPError, SyncClient, SyncHTTPBearerMiddleware


@given('a "{key}" setting on site "{hostname}"')
def create_snippet(context: Any, key: str, hostname: str) -> None:

    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any, Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    payload: Dict[str, Any] = {
        "key": key,
        "hostname": hostname,
        "payload": {},
    }

    if key == "contact":
        payload["payload"] = {"email": "alice@alice.net"}

    try:
        api.setting.post(payload)
    except HTTPError as exc:
        print(exc.response.json)
        raise
