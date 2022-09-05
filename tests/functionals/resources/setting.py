from typing import Any, Dict

from blacksmith import PathInfoField, PostBodyField, Request, Response, register


class GetContactSetting(Request):
    hostname: str = PathInfoField(...)
    key: str = PathInfoField(...)


class ContactSetting(Response):
    email: str


class CreateSetting(Request):
    key: str = PostBodyField(...)
    hostname: str = PathInfoField(...)
    payload: Dict[str, Any] = PostBodyField(...)


register(
    client_name="casualcms",
    resource="setting",
    service="casualcms",
    version=None,
    collection_path="/settings/{hostname}",
    collection_contract={
        "POST": (CreateSetting, None),
    },
)


register(
    client_name="casualcms",
    resource="contact_setting",
    service="casualcms",
    version=None,
    path="/settings/{hostname}/contact",
    contract={
        "GET": (GetContactSetting, ContactSetting),
    },
)
