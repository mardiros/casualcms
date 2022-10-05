from pydantic import BaseModel, Field

from casualcms.domain.model import AbstractSnippet

from casualcms_com.models.atoms.link import Link


class Chapter(BaseModel):
    title: str = Field()
    links: list[Link] = Field(default_factory=list)


class MenuSnippet(AbstractSnippet):
    title: str = Field()
    chapter: list[Chapter] = Field(default_factory=list)

    class Meta:
        template = "snippets/menu.jinja2"
        type = "MenuSnippet"
