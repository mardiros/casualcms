from blacksmith import PostBodyField, Request, register


class CreatePage(Request):
    path: str = PostBodyField(...)
    hostname: str = PostBodyField(...)


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
