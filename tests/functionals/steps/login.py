from typing import Any

from behave import given, then  # type: ignore


@given("anonymous user on the admin page")
def start_fastcms(context: Any):
    context.browser.get("/admin")


@then("I see the login page")
def user_see_page(context: Any):
    username = context.browser.find_element_by_xpath("//input[@placeholder='username']")
    assert username is not None
