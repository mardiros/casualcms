from typing import Any

from behave import when  # type:ignore


@when('I fill the field "{placeholder}" with "{value}"')
def fill_input(context: Any, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field.send_keys(value)


@when('I click on the "{text}" button')
def click_button(context: Any, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//button[contains(text(), "{text}")]')
    el.click()


@when('I click on the "{text}" link')
def click_link(context: Any, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//a[contains(text(), "{text}")]')
    el.click()
