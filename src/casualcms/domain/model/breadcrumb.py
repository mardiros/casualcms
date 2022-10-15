from typing import Sequence

from pydantic import BaseModel, Field


class BreadcrumbItem(BaseModel):
    type: str = Field(default="ListItem", alias="@type")
    position: int = Field(default=0)  # start at 1
    title: str = Field(..., alias="name")
    url: str = Field(default="", alias="item")
    slug: str = Field(..., exclude=True)
    path: str = Field(default="", exclude=True)


class Breadcrumb(BaseModel):
    context: str = Field(default="https://schema.org", alias="@context")
    type: str = Field(default="BreadcrumbList", alias="@type")
    items: Sequence[BreadcrumbItem] = Field(..., alias="itemListElement")
