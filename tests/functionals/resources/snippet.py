from typing import Any, Dict

from blacksmith import PostBodyField, Request, register


class CreateSnippet(Request):
    type: str = PostBodyField(...)
    payload: Dict[str, Any] = PostBodyField(...)


register(
    client_name="casualcms",
    resource="snippet",
    service="casualcms",
    version=None,
    path="/snippets",
    contract={
        "POST": (CreateSnippet, None),
    },
)
