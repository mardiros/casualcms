from typing import Any

from behave import then  # type: ignore

"""
Debug in the devtools of firefox

function getElementByXpath(path) {
  return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}
"""

@then('I see the text "{text}"')
def assert_text(context: Any, text: str):
    text = text.replace("'", "\\'")
    context.browser.find_element_by_xpath(
        f"//*[contains(text(), '{text}') or .='{text}']"
    )
