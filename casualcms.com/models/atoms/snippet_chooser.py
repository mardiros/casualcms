from pydantic import Field

from casualcms.domain.model.block import Block


class SnippetChoice(Block):
    snippet: str = Field()

    class Meta:
        template = "atoms/snippet_chooser.jinja2"
