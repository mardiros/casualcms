from types import NoneType
from typing import Any, Sequence, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.sql.expression import func  # type: ignore

from casualcms.adapters.uow_sqla import orm
from casualcms.adapters.uow_sqla.uow_sqla import (
    AccountSQLRepository,
    AuthnTokenSQLRepository,
    DraftSQLRepository,
    PageSQLRepository,
    SettingSQLRepository,
    SiteSQLRepository,
    SnippetSQLRepository,
    SQLUnitOfWork,
    SQLUnitOfWorkBySession,
)
from casualcms.config import Settings
from casualcms.domain.messages.commands import generate_id
from casualcms.domain.model import AuthnToken, DraftPage, Page, Setting, Site, Snippet
from casualcms.domain.repositories.draft import (
    DraftRepositoryResult,
    DraftSequenceRepositoryResult,
)
from casualcms.service.unit_of_work import AbstractUnitOfWork

from ...casualblog.models import FeatureFlagSetting, HeaderSnippet, HomePage, Link
from .fixtures import (
    fake_account,
    fake_authn_tokens,
    fake_contact_setting,
    fake_draft_page,
    fake_ff_setting,
    fake_footer_snippet,
    fake_header_snippet,
    fake_page,
    fake_site,
    fake_snippet,
)

alice = fake_account(username="alice")
bob = fake_account(username="bob")
dylan = fake_account(username="dylan")
henry = fake_account(username="henry")

draft_hp = fake_draft_page(
    type="blog:HomePage",
    slug="root",
    hero_title="lorem atchoum",
)


cat_page = fake_draft_page(
    type="blog:CategoryPage",
    slug="tech",
    parent=draft_hp.page,
    hero_title="Technologies",
    intro={"title": "tech", "body": "loli pop"},
)


cat2_page = fake_draft_page(
    type="blog:CategoryPage",
    slug="seo",
    parent=draft_hp.page,
    hero_title="SEO",
    intro={"title": "SEO", "body": "You bot"},
)

blog_page = fake_draft_page(
    type="blog:BlogPage",
    slug="seo",
    parent=cat_page.page,
    hero_title="SEO In Tech",
    body=[{"title": "SEO In Tech", "body": "U robot.txt"}],
)


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],
            "non_account": henry,
        }
    ],
)
async def test_account_by_username(
    params: Any, sqla_session: AsyncSession, accounts: NoneType
):
    repo = AccountSQLRepository(sqla_session)
    for account in params["accounts"]:
        acc = await repo.by_username(account.username)
        assert acc.is_ok()
        acc_ok = acc.unwrap()
        assert acc_ok.username == account.username
        assert acc_ok.email == acc_ok.email

    acc = await repo.by_username("henry")
    assert acc.is_err()
    err = acc.unwrap_err()
    assert err.name == "user_not_found"


async def test_account_add(sqla_session: AsyncSession):
    repo = AccountSQLRepository(sqla_session)
    acc = fake_account(username="alice")
    await repo.add(acc)
    assert acc in repo.seen
    assert acc in repo.seen

    qry = select(orm.accounts).filter(orm.accounts.c.id == acc.id)
    accounts_ = await sqla_session.execute(qry)  # type: ignore
    account = accounts_.first()  # type: ignore
    assert account.username == "alice"
    assert account.email == acc.email


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
            "authn_tokens": [fake_authn_tokens(user_id=bob.id)],
        },
    ],
)
async def test_authntoken_by_token(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
    authn_tokens: NoneType,
):
    repo = AuthnTokenSQLRepository(sqla_session)
    tok = await repo.by_token(params["authn_tokens"][0].token)
    assert tok.is_ok()
    tok_ok = tok.unwrap()
    assert tok_ok.id == params["authn_tokens"][0].id
    assert tok_ok.created_at == params["authn_tokens"][0].created_at
    assert tok_ok.expires_at == params["authn_tokens"][0].expires_at
    assert tok_ok.user_id == bob.id
    assert tok_ok.client_addr == "1.2.3.4"
    assert tok_ok.user_agent == "Mozilla/5"

    tok = await repo.by_token("abc")
    assert tok.is_err()
    err = tok.unwrap_err()
    assert err.name == "token_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [bob],  # type: ignore
            "authn_token": fake_authn_tokens(user_id=bob.id),
        },
    ],
)
async def test_authntoken_add(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
):
    authn_token: AuthnToken = params["authn_token"]
    repo = AuthnTokenSQLRepository(sqla_session)
    resp = await repo.add(authn_token)
    assert resp.is_ok()

    qry = select(orm.authn_tokens).filter(orm.authn_tokens.c.id == authn_token.id)
    resp = await sqla_session.execute(qry)  # type: ignore
    orm_token = resp.first()  # type: ignore
    assert orm_token is not None
    assert orm_token.id == authn_token.id
    assert orm_token.token == authn_token.token
    assert orm_token.created_at == authn_token.created_at
    assert orm_token.user_id == authn_token.user_id
    assert orm_token.expires_at == authn_token.expires_at
    assert orm_token.client_addr == authn_token.client_addr
    assert orm_token.user_agent == authn_token.user_agent

    resp = await repo.add(authn_token)
    assert resp.is_err()


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
            "authn_tokens": [fake_authn_tokens(user_id=bob.id)],
        },
    ],
)
async def test_authntoken_delete(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
    authn_tokens: NoneType,
):

    tokens_count = await sqla_session.execute(  # type: ignore
        select(func.count(orm.authn_tokens.c.id)).filter_by(
            token=params["authn_tokens"][0].token
        )
    )
    assert tokens_count.first() == (1,)

    repo = AuthnTokenSQLRepository(sqla_session)
    resp = await repo.remove(params["authn_tokens"][0].token)
    assert resp.is_ok()

    tokens_count = await sqla_session.execute(  # type: ignore
        select(func.count(orm.authn_tokens.c.id)).filter_by(
            token=params["authn_tokens"][0].token
        )
    )
    assert tokens_count.first() == (0,)

    resp = await repo.remove(params["authn_tokens"][0].token)
    assert resp.is_err()
    assert resp.unwrap_err().value == "Unknown token"


@pytest.mark.parametrize(
    "params",
    [
        {
            "id": draft_hp.id,
            "drafts": [draft_hp, cat_page],  # type: ignore
            "expected_slug": "root",
            "expected_path": "/root",
        },
        {
            "id": cat_page.id,
            "drafts": [draft_hp, cat_page, cat2_page],  # type: ignore
            "expected_slug": "tech",
            "expected_path": "/root/tech",
        },
        {
            "id": blog_page.id,
            "drafts": [draft_hp, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slug": "seo",
            "expected_path": "/root/tech/seo",
        },
    ],
)
async def test_draft_by_id(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    root_page: DraftRepositoryResult[HomePage] = await repo.by_id(params["id"])
    assert root_page.is_ok()
    rok = root_page.unwrap()
    assert rok.slug == params["expected_slug"]
    assert rok.path == params["expected_path"]


async def test_draft_by_id_err(sqla_session: AsyncSession):
    repo = DraftSQLRepository(sqla_session)
    root_page: DraftRepositoryResult[HomePage] = await repo.by_id(
        draft_hp.id
    )  # type:ignore
    assert root_page.is_err()
    err = root_page.unwrap_err()
    assert err.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/root",
            "drafts": [draft_hp, cat_page],  # type: ignore
            "expected_slug": "root",
            "expected_id": draft_hp.id,
        },
        {
            "path": "/root/tech",
            "drafts": [draft_hp, cat_page, cat2_page],  # type: ignore
            "expected_slug": "tech",
            "expected_id": cat_page.id,
        },
        {
            "path": "/root/tech/seo",
            "drafts": [draft_hp, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slug": "seo",
            "expected_id": blog_page.id,
        },
    ],
)
async def test_page_by_path(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    root_page: DraftRepositoryResult[HomePage] = await repo.by_path(params["path"])
    assert root_page.is_ok()
    rok = root_page.unwrap()
    assert rok.slug == params["expected_slug"]
    assert rok.path == params["path"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/root",
            "drafts": [draft_hp, cat_page],  # type: ignore
            "expected_slug": "root",
            "expected_id": draft_hp.id,
        }
    ],
)
async def test_page_by_path_err(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    root_page: DraftRepositoryResult[HomePage] = await repo.by_path("/e404")
    assert root_page.is_err()
    err = root_page.unwrap_err()
    assert err.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": None,
            "drafts": [draft_hp, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["root"],
            "expected_ids": [draft_hp.id],
            "expected_paths": ["/root"],
        },
        {
            "parent": "/root",
            "drafts": [draft_hp, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["seo", "tech"],
            "expected_ids": [cat2_page.id, cat_page.id],
            "expected_paths": ["/root/seo", "/root/tech"],
        },
        {
            "parent": "/root/tech",
            "drafts": [draft_hp, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["seo"],
            "expected_ids": [blog_page.id],
            "expected_paths": ["/root/tech/seo"],
        },
        {
            "parent": "/root/seo",
            "drafts": [draft_hp, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": [],
            "expected_ids": [],
            "expected_paths": [],
        },
    ],
)
async def test_page_by_parent(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    child_pages: DraftSequenceRepositoryResult[Any] = await repo.by_parent(
        params["parent"]
    )
    assert child_pages.is_ok()
    ps = child_pages.unwrap()
    assert [p.slug for p in ps] == params["expected_slugs"]
    assert [p.path for p in ps] == params["expected_paths"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": "/foo",
            "drafts": [draft_hp],
        },
        {
            "parent": "/root/foo",
            "drafts": [draft_hp],
        },
    ],
)
async def test_page_by_parent_err(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    child_pages: DraftSequenceRepositoryResult[Any] = await repo.by_parent(
        params["parent"]
    )
    assert child_pages.is_err()
    err = child_pages.unwrap_err()
    assert err.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": None,
            "page": draft_hp,
            "drafts": [],  # type: ignore
            "expected_ancestors": [(draft_hp.id, 0)],
        },
        {
            "parent": draft_hp,
            "page": cat_page,
            "drafts": [draft_hp],  # type: ignore
            "expected_ancestors": [(draft_hp.id, 1), (cat_page.id, 0)],
        },
    ],
)
async def test_page_add(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    await repo.add(params["page"])

    qry = select(orm.drafts).filter(orm.drafts.c.id == params["page"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    page = resp.first()  # type: ignore
    assert page is not None
    assert page.id == params["page"].id

    qry = (
        select(orm.drafts_treepath.c.ancestor_id, orm.drafts_treepath.c.length)
        .filter(orm.drafts_treepath.c.descendant_id == params["page"].id)
        .order_by(orm.drafts_treepath.c.length.desc())
    )

    resp = await sqla_session.execute(qry)  # type: ignore
    assert list(resp) == params["expected_ancestors"]  # type: ignore

    qry = (
        select(orm.drafts_treepath.c.descendant_id, orm.drafts_treepath.c.length)
        .filter(orm.drafts_treepath.c.ancestor_id == params["page"].id)
        .order_by(orm.drafts_treepath.c.length)
    )

    resp = await sqla_session.execute(qry)  # type: ignore
    assert list(resp) == [(params["page"].id, 0)]  # type: ignore


@pytest.mark.parametrize(
    "params",
    [
        {
            "page": draft_hp,
            "update_page": fake_draft_page(
                id=draft_hp.id,
                type="blog:HomePage",
                slug="home",
                title="new title",
                description="new desc",
                hero_title="my new hero",
            ),
            "drafts": [draft_hp, cat_page],  # type: ignore
            "expected_slug": "home",
            "expected_title": "new title",
            "expected_description": "new desc",
            "expected_body": {"body": [], "hero_title": "my new hero"},
        },
    ],
)
async def test_page_update(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)
    await repo.update(params["update_page"])

    qry = select(orm.drafts).filter(orm.drafts.c.id == params["page"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    page: orm.drafts = resp.first()  # type: ignore
    assert page.slug == params["expected_slug"]
    assert page.title == params["expected_title"]
    assert page.description == params["expected_description"]
    assert page.body == params["expected_body"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page],  # type: ignore
        },
    ],
)
async def test_page_remove(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = DraftSQLRepository(sqla_session)

    resp = await repo.remove(draft_hp)
    assert resp.is_err()
    assert resp.unwrap_err().name == "page_has_children"

    resp = await repo.remove(cat2_page)
    assert resp.is_err()
    assert resp.unwrap_err().name == "page_not_found"

    resp = await repo.remove(cat_page)
    assert resp.is_ok()
    assert resp.unwrap() == ...


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(key="snip-this"),
                fake_header_snippet(key="snip-it"),
                fake_header_snippet(key="snip-that"),
            ],
        },
    ],
)
async def test_snippet_by_key(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    rsnippet = await repo.by_key("snip-it")
    assert rsnippet.is_ok()
    snippet = rsnippet.unwrap()
    assert snippet.id == snippets[1].id

    rsnippet = await repo.by_key("e404")
    assert rsnippet.is_err()
    assert rsnippet.unwrap_err().value == "Snippet not found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(id="xyz"),
                fake_header_snippet(id="123"),
                fake_header_snippet(id="abc"),
            ],
        },
    ],
)
async def test_snippet_by_id(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    rsnippet = await repo.by_id("123")
    assert rsnippet.is_ok()
    snippet = rsnippet.unwrap()
    assert snippet.key == snippets[1].key

    rsnippet = await repo.by_id("456")
    assert rsnippet.is_err()
    assert rsnippet.unwrap_err().value == "Snippet not found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippet": fake_snippet("blog:HeaderSnippet", title="Blog"),
        },
    ],
)
async def test_snippet_add(params: Any, sqla_session: AsyncSession):
    repo = SnippetSQLRepository(sqla_session)
    await repo.add(params["snippet"])
    qry = select(orm.snippets).filter(orm.snippets.c.id == params["snippet"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    snippet: orm.snippets = resp.first()  # type: ignore
    assert snippet.key == params["snippet"].key
    assert snippet.body == {
        "title": params["snippet"].title,
        "links": params["snippet"].links,
    }


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(key="snip-this"),
                fake_header_snippet(key="snip-it"),
                fake_header_snippet(key="snip-that"),
            ],
        },
    ],
)
async def test_snippet_remove(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    await repo.remove(snippets[1])

    qry = select(orm.snippets).filter(orm.snippets.c.key == "snip-it")

    resp = await sqla_session.execute(qry)  # type: ignore
    snippet: orm.snippets = resp.first()  # type: ignore
    assert snippet is None

    qry = select(orm.snippets).filter(orm.snippets.c.key == "snip-that")

    resp = await sqla_session.execute(qry)  # type: ignore
    snippet: orm.snippets = resp.first()  # type: ignore
    assert snippet is not None


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(key="snip-this"),
                fake_footer_snippet(key="snip-it"),
                fake_header_snippet(key="snip-that"),
            ],
        },
    ],
)
async def test_snippet_list_filter_type(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    rsnippets = await repo.list(type="blog:HeaderSnippet")
    assert rsnippets.is_ok()
    snips = rsnippets.unwrap()
    sk = [s.key for s in snips]
    assert sk == ["snip-that", "snip-this"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(key="snip-this"),
                fake_header_snippet(key="snip-it"),
                fake_header_snippet(key="snip-that"),
            ],
        },
    ],
)
async def test_snippet_list(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    rsnippets = await repo.list()
    assert rsnippets.is_ok()
    snips = rsnippets.unwrap()
    sk = [s.key for s in snips]
    assert sk == ["snip-it", "snip-that", "snip-this"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(key="snip-this"),
                fake_header_snippet(key="snip-it"),
                fake_header_snippet(key="snip-that"),
            ],
        },
    ],
)
async def test_snippet_update(
    params: Any, sqla_session: AsyncSession, snippets: list[HeaderSnippet]
):
    snippet = snippets[1]
    snippet.key = "new-snip-key"  # type: ignore
    snippet.title = "New title"
    snippet.links = [Link(title="l1", href="/l1")]
    repo = SnippetSQLRepository(sqla_session)
    op = await repo.update(snippet)
    assert op.is_ok()

    qry = select(orm.snippets).filter(orm.snippets.c.id == snippet.id)

    resp = await sqla_session.execute(qry)  # type: ignore
    rsnip: orm.snippets = resp.first()  # type: ignore
    assert rsnip.key == "new-snip-key"
    assert rsnip.body["title"] == "New title"
    assert rsnip.body["links"] == [{"title": "l1", "href": "/l1"}]


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp],
            "site": fake_site(draft_hp),
        },
    ],
)
async def test_site_add(
    params: Any, sqla_session: AsyncSession, drafts: Sequence[DraftPage[Any]]
):
    repo = SiteSQLRepository(sqla_session)
    await repo.add(params["site"])

    qry = select(orm.sites).filter(orm.sites.c.id == params["site"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    site: orm.sites = resp.first()  # type: ignore
    assert site.hostname == params["site"].hostname
    assert site.default == params["site"].default


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(cat_page, hostname="www1"),
                fake_site(cat2_page, hostname="www2"),
            ],
        },
    ],
)
async def test_site_list(
    params: Any,
    sqla_session: AsyncSession,
    drafts: Sequence[DraftPage[Any]],
    sites: Sequence[Site],
):
    repo = SiteSQLRepository(sqla_session)
    rsites = await repo.list()
    assert rsites.is_ok()
    sites_ok = rsites.unwrap()
    ss = [s.hostname for s in sites_ok]
    assert ss == ["www1", "www2"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(cat_page, id="abc"),
                fake_site(cat2_page, id="123"),
            ],
        },
    ],
)
async def test_site_by_id(
    params: Any,
    sqla_session: AsyncSession,
    drafts: Sequence[DraftPage[Any]],
    sites: Sequence[Site],
):
    repo = SiteSQLRepository(sqla_session)
    rsite = await repo.by_id("abc")
    assert rsite.is_ok()
    site_ok = rsite.unwrap()
    assert site_ok.root_page_path == "/root/tech"

    rsite = await repo.by_id("xyz")
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "site_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(cat_page, hostname="www1"),
                fake_site(cat2_page, hostname="www2"),
            ],
        },
    ],
)
async def test_site_by_hostname(
    params: Any,
    sqla_session: AsyncSession,
    drafts: Sequence[DraftPage[Any]],
    sites: Sequence[Site],
):
    repo = SiteSQLRepository(sqla_session)
    rsite = await repo.by_hostname("www1")
    assert rsite.is_ok()
    site_ok = rsite.unwrap()
    assert site_ok.root_page_path == "/root/tech"

    rsite = await repo.by_hostname("www3")
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "site_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(cat_page, hostname="www1"),
                fake_site(cat2_page, hostname="www2"),
            ],
        },
    ],
)
async def test_site_update(
    params: Any,
    sqla_session: AsyncSession,
    drafts: Sequence[DraftPage[Any]],
    sites: Sequence[Site],
):

    site = sites[1]
    site.hostname = "www"
    site.root_page_path = "/root"
    site.default = True
    repo = SiteSQLRepository(sqla_session)
    rsite = await repo.update(site)
    assert rsite.is_ok()

    qry = select(orm.sites).filter(orm.sites.c.id == site.id)
    resp = await sqla_session.execute(qry)  # type: ignore
    updated_site: orm.sites = resp.first()  # type: ignore
    assert updated_site.hostname == "www"
    assert updated_site.default is True
    assert updated_site.draft_id == draft_hp.id

    qry = select(orm.sites).filter(orm.sites.c.id == sites[0].id)
    resp = await sqla_session.execute(qry)  # type: ignore
    not_updated_site: orm.sites = resp.first()  # type: ignore
    assert not_updated_site.hostname == "www1"
    assert not_updated_site.draft_id == cat_page.id

    site.root_page_path = "/e404"
    rsite = await repo.update(site)
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "root_page_not_found"

    site = Site(
        id=generate_id(),
        draft_id=None,
        hostname="x",
        root_page_path="/root",
        default=False,
        secure=False,
    )
    rsite = await repo.update(site)
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "site_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(cat_page, hostname="www1"),
                fake_site(cat2_page, hostname="www2"),
            ],
        },
    ],
)
async def test_site_remove(
    params: Any,
    sqla_session: AsyncSession,
    drafts: Sequence[DraftPage[Any]],
    sites: Sequence[Site],
):
    repo = SiteSQLRepository(sqla_session)
    rsite = await repo.by_hostname("www1")

    await repo.remove(rsite.unwrap())

    rsite = await repo.by_hostname("www1")
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "site_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "setting": fake_ff_setting(title="Blog"),
        },
    ],
)
async def test_setting_add(params: Any, sqla_session: AsyncSession, sites: list[Site]):
    repo = SettingSQLRepository(sqla_session)
    resp = await repo.add(params["setting"])
    assert resp.is_ok()
    qry = select(orm.settings).filter(orm.settings.c.id == params["setting"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    setting: orm.settings = resp.first()  # type: ignore
    assert setting.value == {"use_stuff": True, "use_another_stuff": False}
    assert setting.site_id == sites[0].id


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "settings": [
                fake_ff_setting("www"),
                fake_contact_setting("www"),
                fake_ff_setting("www2"),
            ],
        },
    ],
)
async def test_setting_list(
    params: Any, sqla_session: AsyncSession, settings: list[Setting]
):
    repo = SettingSQLRepository(sqla_session)
    rsettings = await repo.list()
    assert rsettings.is_ok()
    sets = rsettings.unwrap()
    ss = [s.dict() for s in sets]
    ss = [s.dict() for s in sets]
    assert ss == [
        {"email": "bob@alice.net", "hostname": "www"},
        {"hostname": "www", "use_another_stuff": False, "use_stuff": True},
        {"hostname": "www2", "use_another_stuff": False, "use_stuff": True},
    ]


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "settings": [
                fake_ff_setting("www"),
                fake_contact_setting("www"),
                fake_ff_setting("www2"),
            ],
        },
    ],
)
async def test_setting_list_filter_hostname(
    params: Any, sqla_session: AsyncSession, settings: list[Setting]
):
    repo = SettingSQLRepository(sqla_session)
    rsettings = await repo.list(hostname="www")
    assert rsettings.is_ok()
    sets = rsettings.unwrap()
    ss = [s.dict() for s in sets]
    assert ss == [
        {"email": "bob@alice.net", "hostname": "www"},
        {"hostname": "www", "use_another_stuff": False, "use_stuff": True},
    ]


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "settings": [
                fake_ff_setting("www"),
                fake_contact_setting("www"),
                fake_ff_setting("www2"),
            ],
        },
    ],
)
async def test_setting_by_id(
    params: Any, sqla_session: AsyncSession, settings: list[Setting]
):
    repo = SettingSQLRepository(sqla_session)
    rsetting = await repo.by_id(settings[0].id)
    assert rsetting.is_ok()
    setting = rsetting.unwrap()
    assert setting.__meta__.key == "ff"
    assert setting.hostname == "www"

    rsetting = await repo.by_id("456")
    assert rsetting.is_err()
    assert rsetting.unwrap_err().value == "Setting not found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "settings": [
                fake_ff_setting("www"),
                fake_contact_setting("www"),
                fake_ff_setting("www2"),
            ],
        },
    ],
)
async def test_setting_by_key(
    params: Any, sqla_session: AsyncSession, settings: list[Setting]
):
    repo = SettingSQLRepository(sqla_session)
    rsetting = await repo.by_key("www", "ff")
    assert rsetting.is_ok()
    setting = rsetting.unwrap()
    assert setting.id == settings[0].id

    rsetting = await repo.by_key("www2", "contact")
    assert rsetting.is_err()
    assert rsetting.unwrap_err().value == "Setting not found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "settings": [
                fake_ff_setting("www"),
                fake_contact_setting("www"),
                fake_ff_setting("www2"),
            ],
        },
    ],
)
async def test_setting_update(
    params: Any, sqla_session: AsyncSession, sites: list[Site], settings: list[Setting]
):
    setting: FeatureFlagSetting = cast(FeatureFlagSetting, settings[0])
    setting.use_another_stuff = True
    repo = SettingSQLRepository(sqla_session)
    rsetting = await repo.update(setting)
    assert rsetting.is_ok()

    qry = (
        select(orm.settings)
        .filter(orm.settings.c.key == "ff")
        .filter(orm.settings.c.site_id == sites[0].id)
    )
    resp = await sqla_session.execute(qry)  # type: ignore
    orm_setting: orm.settings = resp.first()  # type: ignore
    assert orm_setting.value == {"use_another_stuff": True, "use_stuff": True}

    qry = (
        select(orm.settings)
        .filter(orm.settings.c.key == "ff")
        .filter(orm.settings.c.site_id == sites[1].id)
    )
    resp = await sqla_session.execute(qry)  # type: ignore
    orm_setting: orm.settings = resp.first()  # type: ignore
    assert orm_setting.value == {"use_another_stuff": False, "use_stuff": True}


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [
                fake_site(draft_hp, hostname="www"),
                fake_site(draft_hp, hostname="www2"),
            ],
            "settings": [
                fake_ff_setting("www"),
                fake_contact_setting("www"),
                fake_ff_setting("www2"),
            ],
        },
    ],
)
async def test_setting_remove(
    params: Any, sqla_session: AsyncSession, sites: list[Site], settings: list[Setting]
):
    setting = settings[0]
    repo = SettingSQLRepository(sqla_session)
    rsetting = await repo.remove(setting)
    assert rsetting.is_ok()

    qry = (
        select(orm.settings)
        .filter(orm.settings.c.key == "ff")
        .filter(orm.settings.c.site_id == sites[0].id)
    )
    resp = await sqla_session.execute(qry)  # type: ignore
    orm_setting: orm.settings = resp.first()  # type: ignore
    assert orm_setting is None

    qry = (
        select(orm.settings)
        .filter(orm.settings.c.key == "contact")
        .filter(orm.settings.c.site_id == sites[0].id)
    )
    resp = await sqla_session.execute(qry)  # type: ignore
    orm_setting: orm.settings = resp.first()  # type: ignore
    assert orm_setting is not None

    qry = (
        select(orm.settings)
        .filter(orm.settings.c.key == "ff")
        .filter(orm.settings.c.site_id == sites[1].id)
    )
    resp = await sqla_session.execute(qry)  # type: ignore
    orm_setting: orm.settings = resp.first()  # type: ignore
    assert orm_setting is not None


async def test_sql_uow_by_session_commit(dummy_session: AsyncSession):
    uow = SQLUnitOfWorkBySession(dummy_session)
    await uow.commit()
    assert dummy_session.get_transaction() == "begin_commit"


async def test_sql_uow_by_session_rollback(dummy_session: AsyncSession):
    uow = SQLUnitOfWorkBySession(dummy_session)
    await uow.rollback()
    assert dummy_session.get_transaction() == "begin_rollback"


async def test_sql_uow_by_session_rollback_on_exc(dummy_session: AsyncSession):
    uow = SQLUnitOfWorkBySession(dummy_session)
    try:
        async with uow:
            raise ValueError("Boom")
    except ValueError:
        pass
    assert dummy_session.get_transaction() == "begin_rollback_close"


@pytest.mark.parametrize("method", ["commit", "rollback"])
async def test_sql_uow_runtime_error(method: str, app_settings_sqlite: Settings):
    uow = SQLUnitOfWork(app_settings_sqlite)

    with pytest.raises(RuntimeError) as ctx:
        await getattr(uow, method)()

    assert (
        str(ctx.value)
        == "Bad usage: use the uow from `async with SQLUnitOfWork(settings) as uow`"
    )


@pytest.mark.parametrize("method", ["commit", "rollback"])
async def test_sql_uow_with_runtime_error(method: str, app_settings_sqlite: Settings):
    uow: AbstractUnitOfWork = SQLUnitOfWork(app_settings_sqlite)
    with pytest.raises(RuntimeError) as ctx:
        async with uow as uow:
            pass
    assert str(ctx.value) == "SQLUnitOfWork.initialize() has not been called yet"


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
        },
    ],
)
async def test_sql_uow_account_by_username(
    params: Any, sql_uow: SQLUnitOfWork, accounts_uow: NoneType
):
    async with sql_uow as uow:
        alice_from_uow = await uow.accounts.by_username("alice")
        await uow.rollback()

    assert alice_from_uow.unwrap().id == alice.id

    async with sql_uow as uow:
        alicia_from_uow = await uow.accounts.by_username("alicia")
        await uow.rollback()

    assert alicia_from_uow.unwrap_err().name == "user_not_found"


site_1 = fake_site(draft_hp, hostname="www", secure=True)
site_2 = fake_site(draft_hp, hostname="www2", secure=False)


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [site_1, site_2],
            "pages": [
                fake_page(draft_hp, site_1),
                fake_page(draft_hp, site_2),
                fake_page(cat_page, site_1),
            ],
        },
    ],
)
async def test_sql_uow_page_by_page_id_and_site_id(
    params: Any,
    sqla_session: AsyncSession,
    sql_uow: SQLUnitOfWork,
    pages: Sequence[Page],
):
    repo = PageSQLRepository(sqla_session)

    rpage = await repo.by_draft_page_and_site(draft_hp.id, site_1.id)

    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[0].id

    rpage = await repo.by_draft_page_and_site(draft_hp.id, site_2.id)

    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[1].id

    rpage = await repo.by_draft_page_and_site(cat_page.id, site_1.id)

    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[2].id

    rpage = await repo.by_draft_page_and_site(cat_page.id, site_2.id)

    assert rpage.is_err()
    assert rpage.unwrap_err().name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [site_1, site_2],
            "pages": [
                fake_page(draft_hp, site_1),
                fake_page(draft_hp, site_2),
                fake_page(cat_page, site_1),
            ],
        },
    ],
)
async def test_sql_uow_page_by_url(
    params: Any,
    sqla_session: AsyncSession,
    sql_uow: SQLUnitOfWork,
    pages: Sequence[Page],
):
    repo = PageSQLRepository(sqla_session)

    rpage = await repo.by_url("https://www")
    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[0].id

    rpage = await repo.by_url("https://www/")
    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[0].id

    rpage = await repo.by_url("http://www/")
    assert rpage.is_err()
    assert rpage.unwrap_err().name == "page_not_found"

    rpage = await repo.by_url("http://www2/")
    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[1].id

    rpage = await repo.by_url("https://www/tech")
    assert rpage.is_ok()
    assert rpage.unwrap().id == pages[2].id

    rpage = await repo.by_url("https://www2/tech")
    assert rpage.is_err()
    assert rpage.unwrap_err().name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [site_1, site_2],
            "page": fake_page(draft_hp, site_1),
            "expected": {
                "site_id": site_1.id,
                "draft_id": draft_hp.id,
                "type": "blog:HomePage",
                "template": "homepage.jinja2",
                "path": "//www",
                "title": draft_hp.title,
                "body": draft_hp.page.dict(),
            },
        },
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [site_1, site_2],
            "page": fake_page(cat_page, site_1),
            "expected": {
                "site_id": site_1.id,
                "draft_id": cat_page.id,
                "type": "blog:CategoryPage",
                "template": "category.jinja2",
                "path": "//www/tech",
                "title": cat_page.title,
                "body": cat_page.page.dict(),
            },
        },
    ],
)
async def test_sql_uow_page_add(
    params: Any,
    sqla_session: AsyncSession,
    sql_uow: SQLUnitOfWork,
    drafts: Sequence[DraftPage[Any]],
) -> None:
    page = params["page"]
    repo = PageSQLRepository(sqla_session)
    op_result = await repo.add(page)
    assert op_result.is_ok()
    assert page in repo.seen
    qry = select(orm.pages).filter(orm.pages.c.id == page.id)
    resp = await sqla_session.execute(qry)  # type: ignore
    page = resp.first()  # type: ignore
    assert page.site_id == params["expected"]["site_id"]
    assert page.draft_id == params["expected"]["draft_id"]
    assert page.type == params["expected"]["type"]
    assert page.template == params["expected"]["template"]
    assert page.path == params["expected"]["path"]
    assert page.title == params["expected"]["title"]
    assert page.body == params["expected"]["body"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "drafts": [draft_hp, cat_page, cat2_page],
            "sites": [site_1, site_2],
            "pages": [
                fake_page(draft_hp, site_1),
                fake_page(draft_hp, site_2),
                fake_page(cat_page, site_1),
            ],
        },
    ],
)
async def test_sql_uow_page_update(
    params: Any,
    sqla_session: AsyncSession,
    sql_uow: SQLUnitOfWork,
    pages: Sequence[Page],
):
    page = params["pages"][0]
    page.title = "My new page title"
    page.body = {"body": "my new body"}

    repo = PageSQLRepository(sqla_session)
    op_result = await repo.update(page)
    assert page in repo.seen
    assert op_result.is_ok()

    qry = select(orm.pages).filter(orm.pages.c.id == page.id)
    resp = await sqla_session.execute(qry)  # type: ignore
    updated_page = resp.first()  # type: ignore
    assert updated_page.site_id == page.site.id
    assert updated_page.draft_id == page.draft_id
    assert updated_page.type == page.type
    assert updated_page.template == page.template
    assert updated_page.path == page.path
    assert updated_page.title == page.title
    assert updated_page.body == page.body

    same_draft_other_site = params["pages"][1]
    qry = select(orm.pages).filter(orm.pages.c.id == same_draft_other_site.id)
    resp = await sqla_session.execute(qry)  # type: ignore
    saved_same_draft_other_site = resp.first()  # type: ignore
    assert saved_same_draft_other_site.site_id == site_2.id
    assert saved_same_draft_other_site.draft_id == draft_hp.id
    assert saved_same_draft_other_site.title != page.title
    assert saved_same_draft_other_site.body != page.body

    other_draft_same_site = params["pages"][2]
    qry = select(orm.pages).filter(orm.pages.c.id == other_draft_same_site.id)
    resp = await sqla_session.execute(qry)  # type: ignore
    saved_same_draft_other_site = resp.first()  # type: ignore
    assert saved_same_draft_other_site.site_id == site_1.id
    assert saved_same_draft_other_site.draft_id == cat_page.id
    assert saved_same_draft_other_site.title != page.title
    assert saved_same_draft_other_site.body != page.body
