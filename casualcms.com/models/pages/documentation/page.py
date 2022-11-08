from pydantic import Field

from casualcms.domain.model.abstract_page import AbstractPage

from ...atoms.list_block import ListBlock
from ...atoms.snippet_chooser import SnippetChoice
from ...molecules.paragraph import Paragraph


class DocumentationPage(AbstractPage):

    menu: SnippetChoice | None = Field(None)
    body: ListBlock[Paragraph] = Field(None)

    class Meta:
        parent_types = ["DocumentationHomePage"]
        type = "DocumentationPage"
        template = "pages/documentation/page.jinja2"
