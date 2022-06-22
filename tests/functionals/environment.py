from collections import defaultdict
from typing import Any

from behave import use_fixture  # type: ignore
from fixtures import apicli, browser, casualcms  # type: ignore


def before_scenario(context: Any, scenario: Any):
    port = 6556
    context.stash = defaultdict(dict)
    use_fixture(casualcms, context, port=port)
    use_fixture(browser, context, port=port)
    use_fixture(apicli, context, port=port)
