from typing import Optional

from pydantic import BaseModel, Field

from casualcms.domain.model import Page


class Paragraph(BaseModel):
    title: Optional[str] = Field()
    body: str = Field(widget="textarea")


class HomePage(Page):
    body: list[Paragraph] = []

    class Meta:
        parent_types = None
        template = "homepage.jinja2"
        type = "blog:HomePage"


class CategoryPage(Page):

    intro: Paragraph = Field()

    class Meta:
        parent_types = [HomePage]
        type = "blog:CategoryPage"
        template = "category.jinja2"


class SectionPage(Page):

    intro: Paragraph = Field()

    class Meta:
        parent_types = [HomePage]
        type = "blog:SectionPage"
        template = "section.jinja2"


class BlogPage(Page):

    body: list[Paragraph] = []

    class Meta:
        parent_types = [CategoryPage, "blog:BlogPage"]
        template = "blogpage.jinja2"
