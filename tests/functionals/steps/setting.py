from typing import Any, Dict

from behave import given, then  # type: ignore
from blacksmith import SyncClient, SyncHTTPBearerMiddleware
from hamcrest import assert_that, equal_to  # type: ignore


@given('a "{key}" setting on site "{hostname}"')
def create_setting(context: Any, key: str, hostname: str) -> None:

    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    payload: Dict[str, Any] = {
        "key": key,
        "hostname": hostname,
        "payload": {},
    }

    if key == "contact":
        payload["payload"] = {"email": "alice@alice.net"}

    resp = api.setting.collection_post(payload)
    if resp.is_err():
        exc = resp.unwrap_err()
        print(exc.response.json)
        raise exc


@then('the setting "{key}" on "{hostname}" contains')
def assert_settings(context: Any, key: str, hostname: str):
    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    setting_api = getattr(api, f"{key}_setting")

    rsetting = setting_api.get({"hostname": hostname, "key": key})
    if rsetting.is_err():
        exc = rsetting.unwrap_err()
        print(exc.response.json)
        raise exc
    setting = rsetting.unwrap()
    data = context.table[0]
    assert_that(data.as_dict(), equal_to(setting.model_dump()))
