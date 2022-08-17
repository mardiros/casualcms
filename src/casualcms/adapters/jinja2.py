from abc import ABC, abstractmethod
from typing import Any, Mapping

import pkg_resources
from jinja2 import Environment, FileSystemLoader, Template


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
    def __init__(self, template_search_path: str) -> None:
        super().__init__()
        self.env = Environment(
            loader=FileSystemLoader(build_searchpath(template_search_path)),
            enable_async=True,
        )

    async def include_snippet(self, name: str) -> str:
        # FIXME
        # breakpoint()
        return name

    def get_template(self, template: str) -> Template:
        return self.env.get_template(
            template, globals={"include_snippet": self.include_snippet}
        )

    async def render_template(self, template: str, context: Mapping[str, Any]) -> str:
        tpl = self.get_template(template)
        return await tpl.render_async(**context)
