from typing import Any

from behave import then  # type: ignore


@then('I see the text "{text}"')
def assert_text(context: Any, text: str):
    text = text.replace('"', '\\"')
    context.browser.find_element_by_xpath(f'//*[contains(text(), "{text}")]')
