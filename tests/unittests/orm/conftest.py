from collections import defaultdict
from operator import and_
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)

import pytest
from sqlalchemy import alias, delete, select, text  # type: ignore
from sqlalchemy.engine.cursor import CursorResult  # type: ignore
from sqlalchemy.ext.asyncio import create_async_engine  # type: ignore
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore

from casualcms.adapters.uow_sqla import orm
from casualcms.adapters.uow_sqla.uow_sqla import SQLUnitOfWork
from casualcms.config import Settings
from casualcms.domain.model import (
    AbstractPage,
    Account,
    AuthnToken,
    DraftPage,
    PublishedPage,
    Setting,
    Site,
    Snippet,
)
from casualcms.domain.model.abstract_snippet import Snippet_contra

DATABASE_URL = "sqlite+aiosqlite:///"


@pytest.fixture()
def bared_sqla_engine() -> Iterator[AsyncEngine]:
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    yield engine


@pytest.fixture()
def app_settings_sqlite() -> Iterator[Settings]:
    template_search_path = str((Path(__file__).parent.parent / "templates").resolve())
    yield Settings(
        assets_path=str((Path(__file__).parent.parent / "assets").resolve()),
        template_search_path=template_search_path,
        unit_of_work="casualcms.adapters.uow_sqla:SQLUnitOfWork",
        database_url=DATABASE_URL,
        create_database_schema=True,
        import_models=[],
    )


@pytest.fixture()
async def sqla_engine(
    bared_sqla_engine: AsyncEngine,
) -> AsyncGenerator[AsyncEngine, None]:
    async with bared_sqla_engine.begin() as conn:  # type: ignore
        await conn.run_sync(orm.metadata.create_all)

    yield bared_sqla_engine

    async with bared_sqla_engine.begin() as conn:  # type: ignore
        await conn.run_sync(orm.metadata.drop_all)


@pytest.fixture()
def sqla_session(sqla_engine: AsyncEngine) -> Iterator[AsyncSession]:
    async_session = sessionmaker(sqla_engine, class_=AsyncSession)
    yield async_session()  # type: ignore


@pytest.fixture()
async def accounts(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    accounts: Sequence[Account] = params["accounts"]
    await sqla_session.execute(  # type: ignore
        orm.accounts.insert(),  # type: ignore
        [a.dict() for a in accounts],
    )
    await sqla_session.commit()

    yield None

    await sqla_session.execute(  # type: ignore
        delete(orm.accounts).where(
            orm.accounts.c.username.in_([a.email for a in accounts])
        ),
    )
    await sqla_session.commit()


@pytest.fixture()
async def sites(
    sqla_session: AsyncSession,
    drafts: list[DraftPage[Any]],
    params: Mapping[str, Any],
) -> AsyncGenerator[Sequence[Site], None]:

    sites: Sequence[Site] = params["sites"]
    await sqla_session.execute(  # type: ignore
        orm.sites.insert(),  # type: ignore
        [{"created_at": s.created_at, **s.dict()} for s in sites],
    )
    await sqla_session.commit()

    yield sites

    await sqla_session.execute(  # type: ignore
        delete(orm.sites).where(orm.sites.c.hostname.in_([s.hostname for s in sites])),
    )
    await sqla_session.commit()


@pytest.fixture()
async def authn_tokens(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    authn_tokens: Sequence[AuthnToken] = params["authn_tokens"]
    await sqla_session.execute(  # type: ignore
        orm.authn_tokens.insert(),  # type: ignore
        [t.dict() for t in authn_tokens],
    )
    await sqla_session.commit()

    yield None

    await sqla_session.execute(  # type: ignore
        delete(orm.authn_tokens).where(
            orm.authn_tokens.c.token.in_(  # type: ignore
                [t.token for t in authn_tokens],
            )
        ),
    )
    await sqla_session.commit()


@pytest.fixture()
async def drafts(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[Sequence[DraftPage[Any]], None]:
    def format_page(page: DraftPage[Any]) -> Dict[str, Any]:
        formated_page: Dict[str, Any] = {
            "id": page.id,
            "type": page.type,
            "created_at": page.created_at,
            "slug": page.slug,
            "title": page.title,
            "description": page.description,
            "body": page.page.dict(),
        }
        return formated_page

    async def get_parent_id(page: AbstractPage) -> str:
        page_slugs: list[str] = []
        page_tree = page.parent
        while page_tree:
            page_slugs.append(page_tree.slug)
            page_tree = page_tree.parent
        slugs = enumerate(page_slugs)

        qry = select(orm.drafts)
        for idx, slug in slugs:
            parent = alias(orm.drafts)
            sub = (
                select(orm.drafts_treepath)
                .join(
                    parent,
                    and_(
                        parent.c.id == orm.drafts_treepath.c.ancestor_id,
                        parent.c.slug == slug,
                    ),
                )
                .filter(orm.drafts.c.id == orm.drafts_treepath.c.descendant_id)
                .filter(orm.drafts_treepath.c.length == idx)
            )
            qry = qry.filter(sub.exists())

        res: CursorResult = await sqla_session.execute(qry)
        parent_page: Any = res.first()
        return parent_page.id

    draft_pages: Sequence[DraftPage[Any]] = params["drafts"]
    if draft_pages:
        await sqla_session.execute(  # type: ignore
            orm.drafts.insert(),  # type: ignore
            [format_page(p) for p in draft_pages],
        )

        await sqla_session.execute(  # type: ignore
            orm.drafts_treepath.insert(),  # type: ignore
            [
                {
                    "ancestor_id": p.id,
                    "descendant_id": p.id,
                    "length": 0,
                }
                for p in draft_pages
            ],
        )

        for page in draft_pages:
            # process parents
            # FIXME
            if page.page.parent:
                parent_id = await get_parent_id(page.page)
                # search in the tree path
                await sqla_session.execute(
                    text(
                        """
                        INSERT INTO drafts_treepath(ancestor_id, descendant_id, length)
                        SELECT
                            drafts_treepath.ancestor_id,
                            :draft_id,
                            drafts_treepath.length + 1
                        FROM drafts_treepath
                        WHERE drafts_treepath.descendant_id = :parent_id
                        """
                    ),
                    {"draft_id": page.id, "parent_id": parent_id},
                )

        await sqla_session.commit()

    yield draft_pages

    await sqla_session.execute(  # type: ignore
        delete(orm.drafts_treepath).where(
            orm.drafts_treepath.c.descendant_id.in_([p.id for p in draft_pages])
        ),
    )

    await sqla_session.execute(  # type: ignore
        delete(orm.drafts_treepath).where(
            orm.drafts_treepath.c.ancestor_id.in_([p.id for p in draft_pages])
        ),
    )

    await sqla_session.execute(  # type: ignore
        delete(orm.drafts).where(orm.drafts.c.id.in_([p.id for p in draft_pages])),
    )
    await sqla_session.commit()


@pytest.fixture()
async def snippets(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
) -> AsyncGenerator[Sequence[Snippet[Any]], None]:
    def format_snippet(snippet: Snippet[Snippet_contra]) -> Dict[str, Any]:
        s: Dict[str, Any] = snippet.snippet.dict()
        formated_snippet: Dict[str, Any] = {
            "id": snippet.id,
            "type": snippet.type,
            "created_at": snippet.created_at,
            "key": s.pop("key"),
        }
        formated_snippet["body"] = s
        return formated_snippet

    snippets: Sequence[Snippet[Any]] = params["snippets"]
    if snippets:
        await sqla_session.execute(  # type: ignore
            orm.snippets.insert(),  # type: ignore
            [format_snippet(p) for p in snippets],
        )
        await sqla_session.commit()

    yield snippets

    await sqla_session.execute(  # type: ignore
        delete(orm.snippets).where(orm.snippets.c.id.in_([s.id for s in snippets])),
    )
    await sqla_session.commit()


@pytest.fixture()
async def settings(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
    sites: list[Site],
) -> AsyncGenerator[Sequence[Setting], None]:
    def format_setting(site_id: str, setting: Setting) -> Dict[str, Any]:
        s: Dict[str, Any] = setting.dict(exclude={"hostname"})
        formated_setting: Dict[str, Any] = {
            "id": setting.id,
            "key": setting.__meta__.key,
            "created_at": setting.created_at,
            "site_id": site_id,
        }
        formated_setting["value"] = s
        return formated_setting

    settings: Sequence[Setting] = params["settings"]
    settings_per_hosts: MutableMapping[str, list[Setting]] = defaultdict(list)
    for s in settings:
        settings_per_hosts[s.hostname].append(s)
    for hostname, hsettings in settings_per_hosts.items():
        orm_sites: CursorResult = await sqla_session.execute(
            select(orm.sites).filter_by(hostname=hostname).limit(1)  # type: ignore
        )
        orm_site: Any = orm_sites.first()

        await sqla_session.execute(  # type: ignore
            orm.settings.insert(),  # type: ignore
            [format_setting(orm_site.id, p) for p in hsettings],
        )
        await sqla_session.commit()

    yield settings

    await sqla_session.execute(  # type: ignore
        delete(orm.settings).where(orm.settings.c.id.in_([s.id for s in settings])),
    )
    await sqla_session.commit()


@pytest.fixture()
async def pages(
    sqla_session: AsyncSession,
    params: Mapping[str, Any],
    sites: list[Site],
    drafts: list[DraftPage[Any]],
):
    def format_page(page: PublishedPage[Any]) -> Dict[str, Any]:
        formated_page: Dict[str, Any] = page.dict(exclude={"site", "page"})
        formated_page["id"] = page.id
        formated_page["type"] = page.type
        formated_page["created_at"] = page.created_at
        formated_page["draft_id"] = page.draft_id
        formated_page["site_id"] = page.site.id
        formated_page["title"] = page.title
        formated_page["body"] = page.page.dict()
        return formated_page

    pages = params["pages"]

    await sqla_session.execute(  # type: ignore
        orm.pages.insert(),  # type: ignore
        [format_page(p) for p in pages],
    )
    await sqla_session.commit()

    yield pages

    await sqla_session.execute(  # type: ignore
        delete(orm.pages).where(orm.pages.c.id.in_([p.id for p in pages])),
    )
    await sqla_session.commit()


class DummyAsyncSession:
    def __init__(self):
        self.transaction_state = "begin"

    async def commit(self):
        self.transaction_state += "_commit"

    async def rollback(self):
        self.transaction_state += "_rollback"

    async def close(self):
        self.transaction_state += "_close"

    def get_transaction(self) -> str:  # fake usage
        return self.transaction_state


@pytest.fixture()
def dummy_session():
    return DummyAsyncSession()


@pytest.fixture()
async def sql_uow(app_settings_sqlite: Settings) -> AsyncGenerator[SQLUnitOfWork, None]:
    uow = SQLUnitOfWork(app_settings_sqlite)
    await uow.initialize()
    yield uow
    await uow.dispose()


@pytest.fixture()
async def accounts_uow(
    sql_uow: SQLUnitOfWork,
    params: Mapping[str, Any],
) -> AsyncGenerator[None, None]:

    accounts: Sequence[Account] = params["accounts"]
    async with sql_uow as uow:
        for account in accounts:
            await uow.accounts.add(account)
        await uow.commit()

    yield None
    sqla_session = sql_uow.create_session()  # type: ignore
    await sqla_session.execute(  # type: ignore
        delete(orm.accounts).where(
            orm.accounts.c.username.in_([a.email for a in accounts])
        ),
    )
    await sqla_session.commit()
