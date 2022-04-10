from pydantic import Field

from casualcms.domain.model import Page


class AbstractPage(Page):
    hero_title: str = Field()

    class Meta:
        abstract = True


class RootPage(AbstractPage):
    body: str = Field()

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
