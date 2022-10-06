from pydantic import Field

from casualcms.domain.model import Block


class Link(Block):
    title: str = Field()
    href: str = Field()

    class Meta:
        template = "atoms/link.jinja2"
