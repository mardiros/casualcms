from typing import Any

from behave import when  # type:ignore


@when('I fill the field "{placeholder}" with "{value}"')
def fill_input(context: Any, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field.send_keys(value)


@when('I fill the textarea field "{placeholder}" with "{value}"')
def fill_textarea(context: Any, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//textarea[@placeholder='{placeholder}']"
    )
    field.send_keys(value)


@when('I fill the "{position}" field "{placeholder}" with "{value}"')
def fill_input_pos(context: Any, position: str, placeholder: str, value: str):
    pos = {"first": 0, "second": 1, "third": 2}[position]
    field = context.browser.find_elements_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field[pos].send_keys(value)


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
