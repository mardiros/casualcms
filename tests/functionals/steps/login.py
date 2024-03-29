from typing import Any

from behave import given, then  # type: ignore


@given("anonymous user on the admin page")
def start_fastcms(context: Any):
    context.browser.get("/admin")


@given("user on the admin page")
def start_fastcms_with_login(context: Any):
    # we use the api and fillout the indexeddb using javascript here.
    # we don't test the login form again and again

    api = context.apicli("casualcms")
    rtoken = api.authntoken.post({"username": "alice", "password": "secret"})
    if rtoken.is_err():
        exc = rtoken.unwrap_err()
        print(exc.response.json)
        raise exc
    token = rtoken.unwrap()
    authn = token.model_dump()
    context.browser.get("/admin/login")
    context.browser.add_index_db_value("account", "alice", authn)
    context.browser.add_index_db_value("default", "account", "alice")
    context.browser.get("/admin")


@then("I see the login page")
def assert_user_see_page(context: Any):
    username = context.browser.find_element_by_xpath("//input[@placeholder='username']")
    assert username is not None


@then('I have the default "{key}" set to "{expected_value}"')
def assert_indexeddb_default_value(context: Any, key: str, expected_value: str):

    current_value: str = context.browser.get_index_db_value("default", key) or ""
    assert current_value == expected_value


@then('I have "{table}" "{key}" saved with keys "{keys}"')
def account_saved(context: Any, table: str, key: str, keys: str):
    current_value: dict[str, str] = context.browser.get_index_db_value(table, key) or {}
    expected = {k.strip() for k in keys.split(",")}
    current_keys = set(current_value.keys())
    assert current_keys == expected, f"{current_keys} != {expected}"
