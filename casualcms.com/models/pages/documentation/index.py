from typing import Optional

from pydantic import Field

from casualcms.domain.model.abstract_page import AbstractPage
from casualcms.domain.model.block import Block


class Paragraph(Block):
    title: Optional[str] = Field()
    body: str = Field(widget="textarea")

    class Meta:
        template = "paragraph.jinja2"


class DocumentationHomePage(AbstractPage):
    class Meta:
        parent_types = ["HomePage"]
        type = "DocumentationHomePage"
        template = "pages/documentation/index.jinja2"
