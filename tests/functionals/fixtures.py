import json
import os
import time
import uuid
from multiprocessing import Process
from pathlib import Path
from typing import Any, Callable, Iterator, Optional

from behave import fixture  # type: ignore
from blacksmith import SyncClientFactory, SyncStaticDiscovery, scan
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox

from casualcms.entrypoint import main


class Browser:
    def __init__(self, web_root: str) -> None:
        self.browser = Firefox()
        self.web_root = web_root

        self.db_name = "casualcms"
        self.db_version = 1

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

    def dont_find_element_by_xpath(self, path: str):
        try:
            self.browser.find_element_by_xpath(path)
        except NoSuchElementException:
            return
        else:
            raise ValueError(f"Element {path} exists")

    def find_elements_by_xpath(self, path: str):
        return self.wait_for(self.browser.find_elements_by_xpath, path)  # type: ignore

    def get(self, path: str):
        if path.startswith("/"):
            self.browser.get(f"{self.web_root}{path}")
        else:
            self.browser.get(f"{path}")

    def quit(self):
        self.browser.quit()

    def get_index_db_value(self, table_name: str, key: str) -> Optional[Any]:
        log_id = uuid.uuid1().hex
        self.browser.execute_script(
            """
            var [
                dbName, dbVersion, tableName, searchKey, logId
            ] = [
                arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]
            ];

            var request = window.indexedDB.open(dbName, dbVersion);
            request.onsuccess = function(event) {
                var db = event.target.result;
                var req = db.transaction(
                    tableName, 'readwrite'
                ).objectStore(tableName).get(searchKey)
                req.onsuccess = function(event) {
                    debugNode = document.createElement("code");
                    debugNode.id = logId;
                    debugNode.innerText = JSON.stringify(event.target.result);
                    document.body.appendChild(debugNode);
                };
                req.onerror = function(event) {
                    console.log(event);
                };
            };
            request.onerror = function(event) {
                console.log(event);
            };
            """,
            self.db_name,
            self.db_version,
            table_name,
            key,
            log_id,
        )
        ret = self.wait_for(self.browser.find_element_by_id, log_id)  # type: ignore
        data = json.loads(ret.text)

        self.browser.execute_script(
            """
                var [ logId ] = [ arguments[0] ];

                debugNode = document.getElementById(logId);
                document.body.removeChild(debugNode)
            """,
            log_id,
        )
        return data

    def add_index_db_value(self, table_name: str, key: str, value: Any) -> None:
        self.browser.execute_script(
            """
            var [
                dbName, dbVersion, tableName, searchKey, targetValue
            ] = [
                arguments[0], arguments[1], arguments[2], arguments[3], arguments[4]
            ];
            var request = window.indexedDB.open(dbName, dbVersion);
            request.onsuccess = function(event) {
                var db = event.target.result;
                var objectStore = db.transaction(
                    tableName, 'readwrite'
                ).objectStore(tableName);
                var requestUpdate = objectStore.add(targetValue, searchKey);
                requestUpdate.onsuccess = function(event) {
                    db.commit;
                };
            };
            """,
            self.db_name,
            self.db_version,
            table_name,
            key,
            value,
        )


def run_server(port: int, **kwargs: Any):
    import sys

    p = (Path(__file__).parent.parent).resolve()
    sys.path.append(str(p))
    settings: dict[str, Any] = {
        "bind": f"localhost:{port}",
        "unit_of_work": "casualcms.adapters.uow_inmemory:InMemoryUnitOfWork",
        "admin_username": "alice",
        "admin_password": "secret",
        "import_models": '["casualblog.models"]',
        "template_search_path": str((Path(__file__).parent / "templates").resolve()),
        **kwargs,
    }
    os.environ.update({f"casualcms_{k}": v for k, v in settings.items()})

    main()


@fixture
def casualcms(context: Any, port: int, **kwargs: Any) -> Iterator[None]:
    proc = Process(target=run_server, args=(port,), daemon=True)
    proc.start()
    yield
    proc.kill()


@fixture
def browser(context: Any, port: int, **kwargs: Any) -> Iterator[None]:
    context.browser = Browser(f"http://localhost:{port}")
    yield
    context.browser.quit()


@fixture
def apicli(context: Any, port: int, **kwargs: Any) -> Iterator[None]:
    scan("tests.functionals.resources")
    sd = SyncStaticDiscovery({("casualcms", None): f"http://localhost:{port}/api"})
    context.apicli = SyncClientFactory(sd=sd)
    yield


if __name__ == "__main__":
    run_server(8000, use_reloader="true")
