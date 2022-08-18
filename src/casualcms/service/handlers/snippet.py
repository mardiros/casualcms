from casualcms.domain.messages.commands import CreateSnippet, UpdateSnippet
from casualcms.domain.model.snippet import Snippet, resolve_snippet_type
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_snippet(
    cmd: CreateSnippet,
    uow: AbstractUnitOfWork,
) -> Snippet:
    snip = resolve_snippet_type(cmd.type)
    snippet = snip(
        id=cmd.id,
        slug=cmd.slug,
        created_at=cmd.created_at,
        **cmd.body,
    )
    await uow.snippets.add(snippet)
    return snippet


@listen
async def update_snippet(
    cmd: UpdateSnippet,
    uow: AbstractUnitOfWork,
) -> Snippet | None:

    async with uow as uow:
        snippet = await uow.snippets.by_id(cmd.id)
    if snippet.is_err():
        return
    s = snippet.unwrap()
    if cmd.slug:
        s.slug = cmd.slug
    if cmd.body:
        for key, val in cmd.body.items():
            setattr(s, key, val)
    await uow.snippets.update(s)
    return s
