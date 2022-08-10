from typing import Any, Dict, Optional

from blacksmith import PostBodyField, Request, register


class CreatePage(Request):
    type: str = PostBodyField(...)
    parent: Optional[str] = PostBodyField(None)
    payload: Dict[str, Any] = PostBodyField(...)


register(
    client_name="casualcms",
    resource="page",
    service="casualcms",
    version=None,
    path="/pages",
    contract={
        "POST": (CreatePage, None),
    },
)
