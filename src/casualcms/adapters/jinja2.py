from abc import ABC, abstractmethod
from typing import Any, Mapping, MutableMapping

import pkg_resources
from jinja2 import Environment, FileSystemLoader, Template

from casualcms.domain.model.draft import AbstractPage
from casualcms.service.unit_of_work import AbstractUnitOfWork


def build_searchpath(template_search_path: str) -> list[str]:
    searchpath: list[str] = []
    paths = template_search_path.split(",")
    for path in paths:
        if ":" in path:
            searchpath.append(pkg_resources.resource_filename(*path.split(":", 2)))
        else:
            searchpath.append(path)
    return searchpath


class AbstractTemplateRenderer(ABC):
    @abstractmethod
    async def render_template(self, template: str, context: Mapping[str, Any]) -> str:
        ...


class Jinja2TemplateRender(AbstractTemplateRenderer):
    uow: AbstractUnitOfWork
    """The unit of work used to fetch snippet and settings."""
    hostname: str
    """The hostname of the website that render the website, used to fetch settings."""

    def __init__(
        self, uow: AbstractUnitOfWork, template_search_path: str, hostname: str
    ) -> None:
        super().__init__()
        self.uow = uow
        self.env = Environment(
            loader=FileSystemLoader(build_searchpath(template_search_path)),
            enable_async=True,
        )
        self.hostname = hostname
        self._settings: MutableMapping[str, Any] = {}

    async def include_snippet(self, key: str) -> str:
        rsnippet = await self.uow.snippets.by_key(key)
        if rsnippet.is_ok():
            snippet = rsnippet.unwrap()
            ret = await self.render_template(
                snippet.get_template(), snippet.get_context()
            )
            return ret
        else:
            # should render an error here
            return ""

    async def _try_get_from_cache(self, key: str) -> Any:
        if key in self._settings:
            return self._settings[key]
        rsetting = await self.uow.settings.by_key(self.hostname, key)
        self._settings[key] = rsetting
        return rsetting

    async def get_setting(self, key: str) -> Any:
        key, *subkeys = key.split(".")
        rsettings = await self._try_get_from_cache(key)
        if rsettings.is_err():
            return ""
        settings = rsettings.unwrap().dict()
        for k in subkeys:
            if k in settings:
                settings = settings[k]
            else:
                return ""
        return settings

    def get_template(self, template: str) -> Template:
        return self.env.get_template(
            template,
            globals={
                "include_snippet": self.include_snippet,
                "get_setting": self.get_setting,
            },
        )

    async def render_page(self, template: str, context: AbstractPage) -> str:
        tpl = self.get_template(template)
        return await tpl.render_async(page=context)

    async def render_template(self, template: str, context: Mapping[str, Any]) -> str:
        tpl = self.get_template(template)
        return await tpl.render_async(**context)
