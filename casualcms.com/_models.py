from typing import Optional

from pydantic import BaseModel, Field

from casualcms.domain.model import AbstractPage, AbstractSnippet
from casualcms.domain.model.block import Block


class Link(BaseModel):
    title: str = Field()
    href: str = Field()


class HeaderSnippet(AbstractSnippet):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "header.jinja2"
        type = "HeaderSnippet"


class Paragraph(Block):
    title: Optional[str] = Field()
    body: str = Field(widget="textarea")

    class Meta:
        template = "paragraph.jinja2"


class BasePage(AbstractPage):
    hero_title: str = Field(description="Title of the hero section")

    class Meta:
        abstract = True


class HomePage(BasePage):
    body: list[Paragraph] = Field(default_factory=list)

    class Meta:
        parent_types = None
        template = "index.jinja2"
        type = "HomePage"


class DocumentationNavItem(BaseModel):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)


class DocumentationNav(Block):
    title: str = Field()
    items: list[DocumentationNavItem] = Field(default_factory=list)

    class Meta:
        template = "documentation/menu.jinja2"


class LayoutColumn(BaseModel):
    item: DocumentationNav | Paragraph = Field()


class LayoutColumns(Block):
    items: list[LayoutColumn] = Field(default_factory=list)

    class Meta:
        template = "columns.jinja2"


class DocumentationRootPage(BasePage):

    columns: LayoutColumns = Field()

    class Meta:
        parent_types = [HomePage]
        type = "DocumentationRootPage"
        template = "documentation/index.jinja2"
