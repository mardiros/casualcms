from typing import Any, Dict

from behave import given  # type: ignore
from blacksmith import HTTPError, SyncClient, SyncHTTPBearerMiddleware
from faker import Faker

fake = Faker()


@given('a "{hostname}" site with "{root_page_path}" root page')
def create_site(context: Any, hostname: str, root_page_path: str) -> None:

    account = context.browser.get_index_db_value("account", "alice")
    token: str = account["token"]

    api: SyncClient[Any, Any] = context.apicli("casualcms")
    api.add_middleware(SyncHTTPBearerMiddleware(token))

    payload: Dict[str, Any] = {
        "hostname": hostname,
        "root_page_path": root_page_path,
        "default": False,
        "secure": False,
    }
    print(payload)
    try:
        api.site.post(payload)
    except HTTPError as exc:
        print(exc.response.json)
        raise
