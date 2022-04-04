import logging
from typing import Any, Callable, Coroutine, MutableMapping, Type

import pkg_resources
import venusian  # type: ignore
from fastapi import Depends, FastAPI, Response
from fastapi.routing import APIRouter
from starlette.types import ASGIApp

from casualcms.service.messagebus import MessageRegistry
from casualcms.service.unit_of_work import AbstractUnitOfWork

log = logging.getLogger(__name__)


def resolve(value: str) -> AbstractUnitOfWork:
    """return the attr from the syntax: package.module:attr."""
    ep = pkg_resources.EntryPoint.parse(f"x={value}")
    cls = ep.resolve()
    return cls()


class AppConfig:
    uow: AbstractUnitOfWork
    bus: MessageRegistry

    def __init__(self, settings: MutableMapping[str, Any]):
        self.settings = settings


        if isinstance(self.settings["unit_of_work"], str):
            self.uow = resolve(self.settings["unit_of_work"])
        else:
            self.uow = self.settings["unit_of_work"]

        self.bus = self.settings.get("messagebus") or MessageRegistry()


class FastAPIConfigurator(venusian.Scanner):

    app: FastAPI
    config: AppConfig
    depends = Depends(lambda: FastAPIConfigurator.config)

    def __init__(self, settings: MutableMapping[str, Any]):
        FastAPIConfigurator.config = AppConfig(settings)
        super().__init__(
            app=FastAPI(),
            messagebus=self.config.bus,  # type: ignore
        )

    def __enter__(self) -> "FastAPIConfigurator":
        return self

    def __exit__(
        self,
        exception_type: Type[Exception],
        exception_value: Exception,
        exception_traceback: Any,
    ):
        log.warning("Exiting")
        if exception_value:
            log.error(  # coverage: ignore
                "Unexpected exception while existing: %r" % (exception_value),
                exc_info=exception_traceback,
            )

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Coroutine[Any, Any, Response]],
        *args: Any,
        **kwargs: Any,
    ):
        self.app.add_api_route(path, endpoint, *args, **kwargs)

    def include_router(self, router: APIRouter, *args: Any, **kwargs: Any):
        self.app.include_router(router, *args, **kwargs)

    def mount(self, path: str, app: ASGIApp, name: str):
        self.app.mount(path, app, name)


def configure(
    wrapped: Callable[[FastAPIConfigurator], None]
) -> Callable[[FastAPIConfigurator], None]:
    def callback(
        scanner: venusian.Scanner, name: str, ob: Callable[[venusian.Scanner], None]
    ) -> None:
        if not isinstance(scanner, FastAPIConfigurator):
            return  # coverage: ignore
        ob(scanner)

    venusian.attach(wrapped, callback, category="fastapi")
    return wrapped
