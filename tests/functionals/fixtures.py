import os
import time
from multiprocessing import Process
from pathlib import Path
from typing import Any, Callable

from behave import fixture  # type: ignore
from pydantic import Field
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox

from casualcms.entrypoint import main
from casualcms.domain.model import Page


class HomePage(Page):
    body: str = Field()

    class Meta:
        parent_types = None
        template = "homepage.jinja2"
        type = "blog:HomePage"


class CategoryPage(Page):
    class Meta:
        parent_types = [HomePage]
        type = "blog:CategoryPage"


class SectionPage(Page):
    class Meta:
        parent_types = [HomePage]
        type = "blog:SectionPage"


class BlogPage(Page):
    class Meta:
        parent_types = [CategoryPage, "blog:BlogPage"]


class Browser:
    def __init__(self, web_root: str) -> None:
        self.browser = Firefox()
        self.web_root = web_root

    def wait_for(
        self,
        method: Callable[..., Any],
        *args: Any,
        timeout: int = 10,
        interval: float = 0.2,
    ):
        start_time = time.time()
        while True:
            try:
                return method(*args)
            except (AssertionError, WebDriverException) as exc:
                if time.time() - start_time > timeout:
                    raise exc
                time.sleep(interval)

    def find_element_by_xpath(self, path: str):
        return self.wait_for(self.browser.find_element_by_xpath, path)  # type: ignore

    def get(self, path: str):
        self.browser.get(f"{self.web_root}{path}")

    def quit(self):
        self.browser.quit()


def run_server(port: int, **kwargs: Any):
    settings: dict[str, Any] = {
        "bind": f"localhost:{port}",
        "unit_of_work": "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork",
        "admin_username": "alice",
        "admin_password": "secret",
        "template_search_path": str((Path(__file__).parent / "templates").resolve()),
        **kwargs,
    }
    os.environ.update({f"casualcms_{k}": v for k, v in settings.items()})
    main()


@fixture
def casualcms(context: Any, port: int, **kwargs: Any):
    proc = Process(target=run_server, args=(port,), daemon=True)
    proc.start()
    yield
    proc.kill()


@fixture
def browser(context: Any, port: int, **kwargs: Any):
    context.browser = Browser(f"http://localhost:{port}")
    yield
    context.browser.quit()


if __name__ == "__main__":
    run_server(8000, use_reloader="true")
