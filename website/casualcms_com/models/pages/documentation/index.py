from pydantic import Field

from casualcms.domain.model.abstract_page import AbstractPage

from ...atoms.list_block import ListBlock
from ...atoms.snippet_chooser import SnippetChoice
from ...molecules.card import Card


class DocumentationHomePage(AbstractPage):

    menu: SnippetChoice | None = Field(None)

    cards: ListBlock[Card] | None = Field(None)

    class Meta:
        parent_types = ["HomePage"]
        type = "DocumentationHomePage"
        template = "pages/documentation/index.jinja2"
