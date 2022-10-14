from pydantic import Field

from casualcms.domain.model.abstract_page import AbstractPage

from ...atoms.snippet_chooser import SnippetChoice


class DocumentationHomePage(AbstractPage):

    menu: SnippetChoice | None = Field(None)

    class Meta:
        parent_types = ["HomePage"]
        type = "DocumentationHomePage"
        template = "pages/documentation/index.jinja2"
