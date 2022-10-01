from typing import Optional

from pydantic import BaseModel, Field

from casualcms.domain.model import AbstractPage, Snippet


class Link(BaseModel):
    title: str = Field()
    href: str = Field()


class HeaderSnippet(Snippet):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "header.jinja2"
        type = "HeaderSnippet"


class Paragraph(BaseModel):
    title: Optional[str] = Field()
    body: str = Field(widget="textarea")


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


class DocumentationNav(BaseModel):
    title: str = Field()
    items: list[DocumentationNavItem] = Field(default_factory=list)

    class Meta:
        template = "documentation_nav.jinja2"
        type = "DocumentationNavSnippet"


class LayoutColumn(BaseModel):
    item: DocumentationNav | Paragraph = Field()


class LayoutColumns(BaseModel):
    items: list[LayoutColumn] = Field(default_factory=list)

    class Meta:
        template = "columns.jinja2"
        type = "Columns"


class DocumentationRootPage(BasePage):

    columns: LayoutColumns = Field()

    class Meta:
        parent_types = [HomePage]
        type = "DocumentationRootPage"
        template = "documentation/index.jinja2"


class BlogRootPage(BasePage):

    intro: Optional[Paragraph] = Field()

    class Meta:
        parent_types = [HomePage]
        type = "BlogRootPage"
        template = "blog/index.jinja2"


class BlogPostPage(BasePage):

    body: list[Paragraph] = []
    related_post_snippet: str = ""

    class Meta:
        parent_types = [BlogRootPage, "BlogPostPage"]
        type = "BlogPostPage"
        template = "blog/blogpost.jinja2"
