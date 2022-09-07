from typing import Any

from behave import when  # type:ignore

POSITIONS = {"first": 0, "second": 1, "third": 2}


@when('I fill the field "{placeholder}" with "{value}"')
def fill_input(context: Any, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field.clear()
    field.send_keys(value)


@when('I fill the textarea field "{placeholder}" with "{value}"')
def fill_textarea(context: Any, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//textarea[@placeholder='{placeholder}']"
    )
    field.clear()
    field.send_keys(value)


@when('I fill the "{position}" textarea field "{placeholder}" with "{value}"')
def fill_textarea_pos(context: Any, position: str, placeholder: str, value: str):
    pos = POSITIONS[position]
    field = context.browser.find_elements_by_xpath(
        f"//textarea[@placeholder='{placeholder}']"
    )
    field[pos].clear()
    field[pos].send_keys(value)


@when('I fill the "{position}" field "{placeholder}" with "{value}"')
def fill_input_pos(context: Any, position: str, placeholder: str, value: str):
    pos = POSITIONS[position]
    field = context.browser.find_elements_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field[pos].clear()
    field[pos].send_keys(value)


@when('I click on the "{text}" button')
def click_button(context: Any, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//button[contains(text(), "{text}")]')
    el.click()


@when('I click on the "{position}" button "{text}"')
def click_button_pos(context: Any, position: str, text: str):
    pos = POSITIONS[position]
    text = text.replace('"', '\\"')
    el = context.browser.find_elements_by_xpath(f'//button[contains(text(), "{text}")]')
    el[pos].click()


@when('I click on the "{text}" link')
def click_link(context: Any, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//a[contains(text(), "{text}")]')
    el.click()


@when('I click on the "{position}" link "{text}"')
def click_link_pos(context: Any, position: str, text: str):
    pos = POSITIONS[position]
    text = text.replace('"', '\\"')
    el = context.browser.find_elements_by_xpath(f'//a[contains(text(), "{text}")]')
    el[pos].click()
