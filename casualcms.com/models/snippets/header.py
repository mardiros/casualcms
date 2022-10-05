from pydantic import Field

from casualcms.domain.model import AbstractSnippet

from casualcms_com.models.atoms.link import Link


class HeaderSnippet(AbstractSnippet):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "header.jinja2"
        type = "HeaderSnippet"
