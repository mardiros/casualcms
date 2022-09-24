from typing import Optional

from pydantic import BaseModel, Field

from casualcms.domain.model import DraftPage, Setting, Snippet


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


class AbstractPage(DraftPage):
    hero_title: str = Field(description="Title of the hero section")

    class Meta:
        abstract = True


class HomePage(AbstractPage):
    body: list[Paragraph] = []

    class Meta:
        parent_types = None
        template = "index.jinja2"
        type = "HomePage"


class DocumentationRootPage(AbstractPage):

    intro: Optional[Paragraph] = Field()

    class Meta:
        parent_types = [HomePage]
        type = "DocumentationRootPage"
        template = "documentation/index.jinja2"


class BlogRootPage(AbstractPage):

    intro: Optional[Paragraph] = Field()

    class Meta:
        parent_types = [HomePage]
        type = "BlogRootPage"
        template = "blog/index.jinja2"


class BlogPostPage(AbstractPage):

    body: list[Paragraph] = []
    related_post_snippet: str = ""

    class Meta:
        parent_types = [BlogRootPage, "BlogPostPage"]
        type = "BlogPostPage"
        template = "blog/blogpost.jinja2"
