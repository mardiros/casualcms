from typing import Any, Dict

from behave import given, then  # type: ignore
from blacksmith import HTTPError, SyncClient, SyncHTTPBearerMiddleware


@given('a "{key}" setting on site "{hostname}"')
def create_setting(context: Any, key: str, hostname: str) -> None:

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
        api.setting.collection_post(payload)
    except HTTPError as exc:
        print(exc.response.json)
        raise


@then('the setting "{key}" on "{hostname}" contains')
def assert_settings(context: Any, key: str, hostname: str):
    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any, Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    setting_api = getattr(api, f"{key}_setting")
    try:
        setting = setting_api.get({"hostname": hostname, "key": key})
    except HTTPError as exc:
        print(exc.response.json)
        raise

    data = context.table[0]
    assert data.as_dict() == setting.response.dict()
