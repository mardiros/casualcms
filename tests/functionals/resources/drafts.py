from typing import Any, Dict, Optional

from blacksmith import PostBodyField, Request, register


class CreateDraft(Request):
    type: str = PostBodyField(...)
    parent: Optional[str] = PostBodyField(None)
    payload: Dict[str, Any] = PostBodyField(...)


register(
    client_name="casualcms",
    resource="draft",
    service="casualcms",
    version=None,
    path="/drafts",
    contract={
        "POST": (CreateDraft, None),
    },
)
