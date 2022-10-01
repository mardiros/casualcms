from typing import Optional

from pydantic import BaseModel, Field

from casualcms.domain.model import AbstractPage, Setting
from casualcms.domain.model.abstract_snippet import AbstractSnippet


class Link(BaseModel):
    title: str = Field()
    href: str = Field()


class HeaderSnippet(AbstractSnippet):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "header.jinja2"
        type = "blog:HeaderSnippet"


class FeatureFlagSetting(Setting):
    use_stuff: bool = False
    use_another_stuff: bool | None

    class Meta:
        key = "ff"


class MyAbstractSetting(Setting):
    class Meta:
        abstract = True


class ContactSetting(MyAbstractSetting):
    email: str

    class Meta:
        key = "contact"


class AbstractFooterSnippet(AbstractSnippet):
    class Meta:
        abstract = True


class FooterSnippet(AbstractFooterSnippet):
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "footer.jinja2"


class RelatedPostSnippet(AbstractFooterSnippet):
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "replated_post_snippet.jinja2"
        type = "blog:RelatedPostSnippet"


class Paragraph(BaseModel):
    title: Optional[str] = Field()
    body: str = Field(widget="textarea")


class BasePage(AbstractPage):
    hero_title: str = Field(description="Title of the hero section")

    class Meta:
        abstract = True


class HomePage(BasePage):
    body: list[Paragraph] = []

    class Meta:
        parent_types = None
        template = "homepage.jinja2"
        type = "blog:HomePage"


class CategoryPage(BasePage):

    intro: Optional[Paragraph] = Field()

    class Meta:
        parent_types = [HomePage]
        type = "blog:CategoryPage"
        template = "category.jinja2"


class SectionPage(BasePage):

    intro: Optional[Paragraph] = Field()

    class Meta:
        parent_types = [HomePage]
        type = "blog:SectionPage"
        template = "section.jinja2"


class BlogPage(BasePage):

    body: list[Paragraph] = []
    related_post_snippet: str = ""

    class Meta:
        parent_types = [CategoryPage, "blog:BlogPage"]
        type = "blog:BlogPage"
        template = "blogpage.jinja2"
