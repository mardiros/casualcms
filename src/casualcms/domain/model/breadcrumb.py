from typing import Sequence

from pydantic import BaseModel, Field


class BreadcrumbItem(BaseModel):
    type: str = Field(default="ListItem", alias="@type")
    position: int = Field(...)  # start at 1
    name: str = Field(..., alias="title")
    item: str = Field(..., alias="url")
    slug: str = Field(..., exclude=True)


class Breadcrumb(BaseModel):
    context: str = Field(default="https://schema.org", alias="@context")
    type: str = Field(default="BreadcrumbList", alias="@type")
    items: Sequence[BreadcrumbItem]
