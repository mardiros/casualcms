import time
from typing import Any

from behave import given, when, then  # type: ignore


@given("I wait")
@when("I wait")
@then("I wait")
def i_wait(context: Any):
    time.sleep(60)
