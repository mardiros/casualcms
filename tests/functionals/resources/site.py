from blacksmith import PostBodyField, Request, register


class CreateSite(Request):
    hostname: str = PostBodyField(...)
    root_page_path: str = PostBodyField(...)
    default: bool = PostBodyField(...)
    secure: bool = PostBodyField(...)


register(
    client_name="casualcms",
    resource="site",
    service="casualcms",
    version=None,
    path="/sites",
    contract={
        "POST": (CreateSite, None),
    },
)
