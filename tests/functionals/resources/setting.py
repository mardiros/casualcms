from typing import Any, Dict

from blacksmith import PathInfoField, PostBodyField, Request, register


class CreateSetting(Request):
    key: str = PostBodyField(...)
    hostname: str = PathInfoField(...)
    payload: Dict[str, Any] = PostBodyField(...)


register(
    client_name="casualcms",
    resource="setting",
    service="casualcms",
    version=None,
    path="/settings/{hostname}",
    contract={
        "POST": (CreateSetting, None),
    },
)
