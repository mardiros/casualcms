from casualcms.domain.messages import commands
from casualcms.domain.model import AuthnToken

from .. import unit_of_work
from ..messagebus import listen


@listen
async def create_authn_token(
    cmd: commands.CreateAuthnToken,
    uow: unit_of_work.AbstractUnitOfWork,
) -> AuthnToken:
    token = AuthnToken(
        id=cmd.id,
        token=cmd.token,
        created_at=cmd.created_at,
        expires_at=cmd.expires_at,
        account_id=cmd.account_id,
        client_addr=cmd.client_addr,
        user_agent=cmd.user_agent,
    )
    await uow.authn_tokens.add(token)
    return token
