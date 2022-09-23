from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreateSnippet,
    DeleteSnippet,
    UpdateSnippet,
)
from casualcms.domain.model.snippet import resolve_snippet_type
from casualcms.domain.repositories.snippet import (
    SnippetOperationResult,
    SnippetRepositoryError,
    SnippetRepositoryResult,
)
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_snippet(
    cmd: CreateSnippet,
    uow: AbstractUnitOfWork,
) -> SnippetRepositoryResult:
    snip = resolve_snippet_type(cmd.type)
    snippet = snip(
        id=cmd.id,
        key=cmd.key,
        created_at=cmd.created_at,
        **cmd.body,
    )
    rop = await uow.snippets.add(snippet)
    if rop.is_err():
        return Err(rop.unwrap_err())
    return Ok(snippet)


@listen
async def update_snippet(
    cmd: UpdateSnippet,
    uow: AbstractUnitOfWork,
) -> SnippetOperationResult:

    rsnippet = await uow.snippets.by_id(cmd.id)
    if rsnippet.is_err():
        return Err(rsnippet.unwrap_err())
    snippet = rsnippet.unwrap()
    if cmd.key:
        snippet.key = cmd.key
    if cmd.body:
        for key, val in cmd.body.items():
            setattr(snippet, key, val)
    return await uow.snippets.update(snippet)


@listen
async def delete_snippet(
    cmd: DeleteSnippet,
    uow: AbstractUnitOfWork,
) -> SnippetOperationResult:
    snippet = await uow.snippets.by_id(cmd.id)
    if snippet.is_err():
        return Err(SnippetRepositoryError.snippet_not_found)
    s = snippet.unwrap()
    return await uow.snippets.remove(s)
