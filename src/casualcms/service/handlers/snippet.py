from typing import Any

from result import Err, Ok

from casualcms.domain.messages.commands import (
    CreateSnippet,
    DeleteSnippet,
    UpdateSnippet,
)
from casualcms.domain.model import resolve_snippet_type
from casualcms.domain.model.abstract_snippet import Snippet_contra
from casualcms.domain.model.snippet import Snippet
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
) -> SnippetRepositoryResult[Snippet_contra]:
    rsnip = resolve_snippet_type(cmd.type)
    if rsnip.is_err():
        return Err(SnippetRepositoryError.snippet_type_not_found)
    snip = rsnip.unwrap()
    rsnippet = snip(
        id=cmd.id,
        key=cmd.key,
        created_at=cmd.created_at,
        **cmd.body,
    )
    snippet: Snippet[Any] = Snippet(snippet=rsnippet)
    rop = await uow.snippets.add(snippet)
    if rop.is_err():
        return Err(rop.unwrap_err())
    return Ok(snippet)


@listen
async def update_snippet(
    cmd: UpdateSnippet,
    uow: AbstractUnitOfWork,
) -> SnippetOperationResult:

    rsnippet: SnippetRepositoryResult[Any] = await uow.snippets.by_id(cmd.id)
    if rsnippet.is_err():
        return Err(rsnippet.unwrap_err())
    snippet_wrapper = rsnippet.unwrap()
    snippet = snippet_wrapper.snippet
    if cmd.key:
        snippet.key = cmd.key
    if cmd.body:
        for key, val in cmd.body.items():
            setattr(snippet, key, val)
    return await uow.snippets.update(snippet_wrapper)


@listen
async def delete_snippet(
    cmd: DeleteSnippet,
    uow: AbstractUnitOfWork,
) -> SnippetOperationResult:
    snippet: SnippetRepositoryResult[Any] = await uow.snippets.by_id(cmd.id)
    if snippet.is_err():
        return Err(SnippetRepositoryError.snippet_not_found)
    s = snippet.unwrap()
    return await uow.snippets.remove(s)
