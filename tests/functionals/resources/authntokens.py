from blacksmith import PostBodyField, Request, Response, register


class AuthnToken(Response):
    token: str
    user_id: str
    username: str
    expires_at: str
    lang: str


class CreateToken(Request):
    username: str = PostBodyField(...)
    password: str = PostBodyField(...)


register(
    client_name="casualcms",
    resource="authntoken",
    service="casualcms",
    version=None,
    path="/authntokens",
    contract={
        "POST": (CreateToken, AuthnToken),
    },
)
