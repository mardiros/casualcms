from casualcms_com.models.atoms.link import Link
from pydantic import Field

from casualcms.domain.model import AbstractSnippet


class HeaderSnippet(AbstractSnippet):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "snippets/header.jinja2"
        type = "HeaderSnippet"
        title = "📰 Header Snippet"
