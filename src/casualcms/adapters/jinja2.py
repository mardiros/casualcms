from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Mapping, MutableMapping, MutableSet, cast

import pkg_resources
from jinja2 import Environment, FileSystemLoader, Template
from markupsafe import Markup
from pygments import highlight  # type: ignore
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from casualcms.domain.model import AbstractPage
from casualcms.domain.model.abstract_snippet import AbstractSnippet
from casualcms.domain.model.block import Block, CodeBlock
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
    async def include_block(
        self, block: Block, page: AbstractPage, **kwargs: Any
    ) -> str:
        ...

    @abstractmethod
    async def render_page(self, page: AbstractPage) -> str:
        ...

    @abstractmethod
    async def render_snippet(self, snippet: AbstractSnippet, page: AbstractPage) -> str:
        ...

    @abstractmethod
    async def render_block(self, block: Block, page: AbstractPage) -> str:
        ...

    @abstractmethod
    async def render_codeblock(
        self, block: CodeBlock, page: AbstractPage, **kwargs: Any
    ) -> str:
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
        self._formatter: MutableMapping[int, MutableSet[str]] = {}

    async def include_block(
        self, block: Block, page: AbstractPage, **kwargs: Any
    ) -> str:
        if block is None:
            return ""
        if isinstance(block, CodeBlock):
            ret = await self.render_codeblock(block=block, page=page, **kwargs)
        else:
            ret = await self.render_block(block=block, page=page, **kwargs)
        return ret

    async def include_snippet(self, key: str, page: AbstractPage, **kwargs: Any) -> str:
        rsnippet = await self.uow.snippets.by_key(key)
        if rsnippet.is_ok():
            snippet = rsnippet.unwrap()
            ret = await self.render_snippet(
                snippet=snippet.snippet, page=page, **kwargs
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
        settings = rsettings.unwrap().setting.model_dump()
        for k in subkeys:
            if k in settings:
                settings = settings[k]
            else:
                return ""
        return settings

    def get_template(self, page: AbstractPage, template: str) -> Template:
        return self.env.get_template(
            template,
            globals={
                "include_block": partial(self.include_block, page=page),
                "include_snippet": partial(self.include_snippet, page=page),
                "get_setting": self.get_setting,
            },
        )

    async def render_page(self, page: AbstractPage) -> str:
        self._formatter[id(page)] = set()
        tpl = self.get_template(page, page.__meta__.template)
        ret = await tpl.render_async(page=page)
        del self._formatter[id(page)]
        return ret

    async def render_snippet(
        self, snippet: AbstractSnippet, page: AbstractPage, **kwargs: Any
    ) -> str:
        tpl = self.get_template(page, snippet.__meta__.template)
        return await tpl.render_async(snippet=snippet, page=page, **kwargs)

    async def render_block(
        self,
        block: Block,
        page: AbstractPage,
        **kwargs: Any,
    ) -> str:
        tpl = self.get_template(page, block.__meta__.template)
        return await tpl.render_async(block=block, page=page, **kwargs)

    async def render_codeblock(
        self, block: CodeBlock, page: AbstractPage, **kwargs: Any
    ) -> str:
        lexer = get_lexer_by_name(block.language)

        xtra = cast(Mapping[str, Any], block.model_fields["code"].json_schema_extra)
        formatter: HtmlFormatter[Any] = xtra.get("formatter") or HtmlFormatter()
        formatters: MutableSet[str] = self._formatter[id(page)]
        fmt = formatter.style.__class__
        name = f"{fmt.__module__}:{fmt.__qualname__}"
        if name in formatters:
            return Markup(highlight(block.code, lexer, formatter))
        else:
            formatters.add(name)
            style_output: str = f"<style>{formatter.get_style_defs()}</style>"
            return Markup(f"{style_output}{highlight(block.code, lexer, formatter)}")
