from pydantic import Field

from casualcms.domain.model import AbstractPage


class HomePage(AbstractPage):
    hero_title: str = Field(description="Title of the hero section")

    class Meta:
        parent_types = None
        template = "pages/index.jinja2"
        type = "HomePage"
