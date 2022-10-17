from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

from casualcms.domain.model import (
    AbstractPage,
    AbstractSetting,
    AbstractSnippet,
    Block,
    GenericBlock,
)


class Link(BaseModel):
    title: str = Field()
    href: str = Field()


class Box(Block):
    title: str = Field()
    paragraph: str = Field()

    class Meta:
        template = "box.jinja2"
        title = "Paragraph in box"


class HeaderSnippet(AbstractSnippet):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)

    class Meta:
        template = "header.jinja2"
        type = "blog:HeaderSnippet"


class FeatureFlagSetting(AbstractSetting):
    use_stuff: bool = False
    use_another_stuff: bool | None

    class Meta:
        key = "ff"
        title = "Feature Flag"


class MyAbstractSetting(AbstractSetting):
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
        title = "Footer Snippet"


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
        title = "🏠 Home Page"


class CategoryPage(BasePage):

    intro: Optional[Paragraph] = Field(default=None)

    class Meta:
        parent_types = [HomePage]
        type = "blog:CategoryPage"
        template = "category.jinja2"


class BlockInSnippet(Block):
    title: str

    class Meta:
        template = "snippet_block.jinja2"


class SnippetBlock(AbstractSnippet):
    title: str
    box: BlockInSnippet

    class Meta:
        template = "snippet_box.jinja2"
        type = "blog:SnippetBlock"


class SnippetBlockPage(AbstractPage):
    class Meta:
        template = "page_with_snippet_block.jinja2"
        type = "blog:SnippetBlockPage"


T = TypeVar("T")


class ListBlock(GenericBlock, Generic[T]):
    items: list[T] = Field(default_factory=list)

    class Meta:
        template = "list_block.jinja2"


class SectionPage(BasePage):

    intro: Optional[Paragraph] = Field()
    box: Box = Field()
    boxes: ListBlock[Box] = Field(default_factory=ListBlock)

    class Meta:
        parent_types = [HomePage]
        type = "blog:SectionPage"
        template = "section.jinja2"


K = TypeVar("K")
V = TypeVar("V")


class DefinitionBlock(Block):
    body: str = Field(widget="textarea")

    class Meta:
        template = "definition.jinja2"


class StructBlock(GenericBlock, Generic[K, V]):
    items: dict[K, V] = Field(default_factory=dict)

    class Meta:
        template = "struct_block.jinja2"


class GlossaryPage(BasePage):

    words: StructBlock[str, DefinitionBlock] = Field(default_factory=StructBlock)

    class Meta:
        parent_types = ["blog:SectionPage"]
        type = "blog:GlossaryPage"
        template = "glossary.jinja2"


class BlogPage(BasePage):

    body: list[Paragraph] = []
    related_post_snippet: str = ""

    class Meta:
        parent_types = [CategoryPage, "blog:BlogPage"]
        type = "blog:BlogPage"
        template = "blogpage.jinja2"
