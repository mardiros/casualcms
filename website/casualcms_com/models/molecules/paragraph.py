from typing import Literal

from pydantic import Field
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name  # type: ignore

from casualcms.domain.model.block import Block, CodeBlock

from ..atoms.rich_text import RichText


class PyCodeBlock(CodeBlock):
    language: Literal["Python"] = Field(default="hidden", widget="hidden")

    class Meta:
        formatter = HtmlFormatter(  # type: ignore
            # linenos="inline",
            style=get_style_by_name("manni"),
        )


class Paragraph(Block):
    anchor: str = Field()
    title: str = Field()
    body: list[RichText | PyCodeBlock] = []

    class Meta:
        template = "molecules/paragraph.jinja2"
