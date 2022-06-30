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
    class Meta:
        parent_types = [HomePage]
        type = "blog:CategoryPage"


class SectionPage(Page):
    class Meta:
        parent_types = [HomePage]
        type = "blog:SectionPage"


class BlogPage(Page):
    class Meta:
        parent_types = [CategoryPage, "blog:BlogPage"]
