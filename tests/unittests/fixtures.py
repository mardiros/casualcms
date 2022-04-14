from typing import Optional
from pydantic import Field, BaseModel

from casualcms.domain.model import Page


class Paragraph(BaseModel):
    title: Optional[str] = Field()
    body: str = Field()


class AbstractPage(Page):
    hero_title: str = Field(description="Title of the hero section")

    class Meta:
        abstract = True


class RootPage(AbstractPage):
    body: list[Paragraph] = []

    class Meta:
        parent_types = None
        template = "page.jinja2"


class CategoryPage(Page):
    class Meta:
        parent_types = [RootPage]
        type = "casual:CategoryPage"


class SectionPage(Page):
    class Meta:
        parent_types = [RootPage]
        type = "casual:SectionPage"


class BlogPage(Page):
    class Meta:
        parent_types = [CategoryPage, "casual:SectionPage"]
