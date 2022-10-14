from pydantic import Field

from casualcms.domain.model.abstract_page import AbstractPage

from ...atoms.snippet_chooser import SnippetChoice


class DocumentationPage(AbstractPage):

    menu: SnippetChoice | None = Field(None)

    class Meta:
        parent_types = ["DocumentationHomePage"]
        type = "DocumentationPage"
        template = "pages/documentation/page.jinja2"
