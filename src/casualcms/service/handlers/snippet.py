from casualcms.domain.messages.commands import CreateSnippet
from casualcms.domain.model.snippet import Snippet, resolve_type
from casualcms.service.messagebus import listen
from casualcms.service.unit_of_work import AbstractUnitOfWork


@listen
async def create_snippet(
    cmd: CreateSnippet,
    uow: AbstractUnitOfWork,
) -> Snippet:
    snip = resolve_type(cmd.type)
    snippet = snip(
        id=cmd.id,
        slug=cmd.slug,
        created_at=cmd.created_at,
        **cmd.body,
    )
    await uow.snippets.add(snippet)
    return snippet
