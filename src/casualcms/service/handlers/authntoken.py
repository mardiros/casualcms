from result import Err, Ok

from casualcms.domain.messages import commands
from casualcms.domain.model import AuthnToken
from casualcms.domain.repositories.authntoken import (
    AuthnTokenOperationResult,
    AuthnTokenRepositoryResult,
)

from .. import unit_of_work
from ..messagebus import listen


@listen
async def create_authn_token(
    cmd: commands.CreateAuthnToken,
    uow: unit_of_work.AbstractUnitOfWork,
) -> AuthnTokenRepositoryResult:
    token = AuthnToken(
        id=cmd.id,
        token=cmd.token,
        created_at=cmd.created_at,
        expires_at=cmd.expires_at,
        user_id=cmd.user_id,
        client_addr=cmd.client_addr,
        user_agent=cmd.user_agent,
    )
    resp = await uow.authn_tokens.add(token)
    if resp.is_err():
        return Err(resp.unwrap_err())
    return Ok(token)


@listen
async def delete_authn_token(
    cmd: commands.DeleteAuthnToken,
    uow: unit_of_work.AbstractUnitOfWork,
) -> AuthnTokenOperationResult:
    return await uow.authn_tokens.remove(cmd.token)
