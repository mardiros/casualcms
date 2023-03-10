from pydantic import Field

from casualcms.domain.model import Block

from ..atoms.link import Link


class Card(Block):
    title: str = Field(...)
    content: str = Field(widget="richtext")
    footer_links: list[Link] = Field(...)

    class Meta:
        template = "molecules/card.jinja2"
