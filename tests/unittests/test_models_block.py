from typing import Any, Mapping

import pytest

from tests.casualblog.models import BlockInSnippet, Box


@pytest.mark.parametrize(
    "params",
    [
        {
            "block": Box,
            "expected_schema": {
                "properties": {
                    "paragraph": {
                        "title": "Paragraph",
                        "type": "string",
                        "ui:widget": "textarea",
                    },
                    "title": {"title": "Title", "type": "string"},
                },
                "required": ["title", "paragraph"],
                "title": "Paragraph in box",
                "type": "object",
            },
        },
        {
            "block": BlockInSnippet,
            "expected_schema": {
                "properties": {"title": {"title": "Title", "type": "string"}},
                "required": ["title"],
                "title": "Block In Snippet",
                "type": "object",
            },
        },
    ],
)
def test_block_schema(params: Mapping[str, Any]):
    schema = params["block"].model_json_schema()
    assert schema == params["expected_schema"]
