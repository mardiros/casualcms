from behave import when  # type:ignore
from tests.functionals.typing import Context

POSITIONS = {"first": 0, "second": 1, "third": 2}


@when('I fill the field "{placeholder}" with "{value}"')
def fill_input(context: Context, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field.clear()
    field.send_keys(value)


@when('I fill the textarea field "{placeholder}" with "{value}"')
def fill_textarea(context: Context, placeholder: str, value: str):
    field = context.browser.find_element_by_xpath(
        f"//textarea[@placeholder='{placeholder}']"
    )
    field.clear()
    field.send_keys(value)


@when('I fill the "{position}" textarea field "{placeholder}" with "{value}"')
def fill_textarea_pos(context: Context, position: str, placeholder: str, value: str):
    pos = POSITIONS[position]
    field = context.browser.find_elements_by_xpath(
        f"//textarea[@placeholder='{placeholder}']"
    )
    field[pos].clear()
    field[pos].send_keys(value)


@when('I fill the "{position}" field "{placeholder}" with "{value}"')
def fill_input_pos(context: Context, position: str, placeholder: str, value: str):
    pos = POSITIONS[position]
    field = context.browser.find_elements_by_xpath(
        f"//input[@placeholder='{placeholder}']"
    )
    field[pos].clear()
    field[pos].send_keys(value)


@when('I click on the "{text}" button')
def click_button(context: Context, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//button[contains(text(), "{text}")]')
    el.click()


@when('I click on the "{position}" button "{text}"')
def click_button_pos(context: Context, position: str, text: str):
    pos = POSITIONS[position]
    text = text.replace('"', '\\"')
    el = context.browser.find_elements_by_xpath(f'//button[contains(text(), "{text}")]')
    el[pos].click()


@when('I click on the "{text}" button having the role "{role}"')
def click_button_with_role(context: Context, text: str, role: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(
        f'//button[@role="{role}" and contains(text(), "{text}")]'
    )
    el.click()


@when('I click on the "{text}" link')
def click_link(context: Context, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//a[contains(text(), "{text}")]')
    el.click()


@when('I click on the "{text}" label')
def click_label(context: Context, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(
        f'//label/span[contains(text(), "{text}")]'
    )
    el.click()


@when('I click on the "{position}" link "{text}"')
def click_link_pos(context: Context, position: str, text: str):
    pos = POSITIONS[position]
    text = text.replace('"', '\\"')
    el = context.browser.find_elements_by_xpath(f'//a[contains(text(), "{text}")]')
    el[pos].click()


@when('I click on the "{text}" link ignoring the target attribute')
def click_link_target_blank(context: Context, text: str):
    text = text.replace('"', '\\"')
    el = context.browser.find_element_by_xpath(f'//a[contains(text(), "{text}")]')
    context.browser.remove_target_blank(f'//a[contains(text(), "{text}")]')
    el.click()
