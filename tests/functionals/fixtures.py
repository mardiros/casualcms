import time
from multiprocessing import Process
from typing import Any, Callable

import uvicorn  # type: ignore
from behave import fixture  # type: ignore
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox


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
    uvicorn.run("casualcms.entrypoint:app", port=port, **kwargs)


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
    run_server(8000, reload=True)
