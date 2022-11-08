from pydantic import Field

from casualcms.domain.model.block import Block


class RichText(Block):
    body: str = Field(
        widget="richtext",
        features=[
            "bold",
            "italic",
            "link",
            "h3",
            "h4",
            "h5",
            "blockquote",
            "ul",
            "ol",
        ],
    )

    class Meta:
        template = "atoms/rich_text.jinja2"
