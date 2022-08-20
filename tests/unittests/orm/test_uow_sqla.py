from types import NoneType
from typing import Any, Sequence

import pytest
from sqlalchemy import delete  # type: ignore
from sqlalchemy import text  # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy.future import select  # type: ignore
from sqlalchemy.sql.expression import func  # type: ignore

from casualcms.adapters.uow_sqla import orm
from casualcms.adapters.uow_sqla.uow_sqla import (
    AccountSQLRepository,
    AuthnTokenSQLRepository,
    PageSQLRepository,
    SiteSQLRepository,
    SnippetSQLRepository,
    SQLUnitOfWork,
    SQLUnitOfWorkBySession,
)
from casualcms.config import Settings
from casualcms.domain.messages.commands import generate_id
from casualcms.domain.model.page import Page
from casualcms.domain.model.site import Site
from casualcms.domain.model.snippet import Snippet
from casualcms.service.unit_of_work import AbstractUnitOfWork

from ...casualblog.models import HeaderSnippet, Link
from .fixtures import (
    fake_account,
    fake_authn_tokens,
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

home_page = fake_page(
    type="blog:HomePage",
    slug="root",
    hero_title="lorem atchoum",
)


cat_page = fake_page(
    type="blog:CategoryPage",
    slug="tech",
    parent=home_page,
    hero_title="Technologies",
    intro={"title": "tech", "body": "loli pop"},
)


cat2_page = fake_page(
    type="blog:CategoryPage",
    slug="seo",
    parent=home_page,
    hero_title="SEO",
    intro={"title": "SEO", "body": "You bot"},
)

blog_page = fake_page(
    type="blog:BlogPage",
    slug="seo",
    parent=cat_page,
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

    accounts_ = await sqla_session.execute(  # type: ignore
        text("SELECT username, email FROM accounts where id = :id"), {"id": acc.id}
    )
    account = accounts_.first()  # type: ignore
    assert account.username == "alice"
    assert account.email == acc.email


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
            "authn_tokens": [fake_authn_tokens(account_id=bob.id)],
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
    assert tok_ok.account_id == bob.id
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
            "authn_token": fake_authn_tokens(account_id=bob.id),
        },
    ],
)
async def test_authntoken_add(
    params: Any,
    sqla_session: AsyncSession,
    accounts: NoneType,
):
    repo = AuthnTokenSQLRepository(sqla_session)
    await repo.add(params["authn_token"])
    tok = await repo.by_token(params["authn_token"].token)
    assert tok.is_ok()
    token_ok = tok.unwrap()
    assert token_ok.id == params["authn_token"].id
    await sqla_session.execute(  # type: ignore
        delete(orm.authn_tokens).where(orm.authn_tokens.c.id == token_ok.id),
    )


@pytest.mark.parametrize(
    "params",
    [
        {
            "accounts": [alice, bob, dylan],  # type: ignore
            "authn_tokens": [fake_authn_tokens(account_id=bob.id)],
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
    await repo.remove(params["authn_tokens"][0].token)

    tokens_count = await sqla_session.execute(  # type: ignore
        select(func.count(orm.authn_tokens.c.id)).filter_by(
            token=params["authn_tokens"][0].token
        )
    )
    assert tokens_count.first() == (0,)


@pytest.mark.parametrize(
    "params",
    [
        {
            "id": home_page.id,
            "pages": [home_page, cat_page],  # type: ignore
            "expected_slug": "root",
            "expected_path": "/root",
        },
        {
            "id": cat_page.id,
            "pages": [home_page, cat_page, cat2_page],  # type: ignore
            "expected_slug": "tech",
            "expected_path": "/root/tech",
        },
        {
            "id": blog_page.id,
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slug": "seo",
            "expected_path": "/root/tech/seo",
        },
    ],
)
async def test_page_by_id(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    root_page = await repo.by_id(params["id"])
    assert root_page.is_ok()
    rok = root_page.unwrap()
    assert rok.slug == params["expected_slug"]
    assert rok.path == params["expected_path"]


async def test_page_by_id_err(sqla_session: AsyncSession):
    repo = PageSQLRepository(sqla_session)
    root_page = await repo.by_id(home_page.id)
    assert root_page.is_err()
    err = root_page.unwrap_err()
    assert err.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/root",
            "pages": [home_page, cat_page],  # type: ignore
            "expected_slug": "root",
            "expected_id": home_page.id,
        },
        {
            "path": "/root/tech",
            "pages": [home_page, cat_page, cat2_page],  # type: ignore
            "expected_slug": "tech",
            "expected_id": cat_page.id,
        },
        {
            "path": "/root/tech/seo",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slug": "seo",
            "expected_id": blog_page.id,
        },
    ],
)
async def test_page_by_path(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    root_page = await repo.by_path(params["path"])
    assert root_page.is_ok()
    rok = root_page.unwrap()
    assert rok.slug == params["expected_slug"]
    assert rok.path == params["path"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "path": "/root",
            "pages": [home_page, cat_page],  # type: ignore
            "expected_slug": "root",
            "expected_id": home_page.id,
        }
    ],
)
async def test_page_by_path_err(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    root_page = await repo.by_path("/e404")
    assert root_page.is_err()
    err = root_page.unwrap_err()
    assert err.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": None,
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["root"],
            "expected_ids": [home_page.id],
            "expected_paths": ["/root"],
        },
        {
            "parent": "/root",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["seo", "tech"],
            "expected_ids": [cat2_page.id, cat_page.id],
            "expected_paths": ["/root/seo", "/root/tech"],
        },
        {
            "parent": "/root/tech",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["seo"],
            "expected_ids": [blog_page.id],
            "expected_paths": ["/root/tech/seo"],
        },
        {
            "parent": "/root/seo",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": [],
            "expected_ids": [],
            "expected_paths": [],
        },
    ],
)
async def test_page_by_parent(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    child_pages = await repo.by_parent(params["parent"])
    assert child_pages.is_ok()
    ps = child_pages.unwrap()
    assert [p.slug for p in ps] == params["expected_slugs"]
    assert [p.path for p in ps] == params["expected_paths"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": "/foo",
            "pages": [home_page],
        },
        {
            "parent": "/root/foo",
            "pages": [home_page],
        },
    ],
)
async def test_page_by_parent_err(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    child_pages = await repo.by_parent(params["parent"])
    assert child_pages.is_err()
    err = child_pages.unwrap_err()
    assert err.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": None,
            "page": home_page,
            "pages": [],  # type: ignore
            "expected_ancestors": [(home_page.id, 0)],
        },
        {
            "parent": home_page,
            "page": cat_page,
            "pages": [home_page],  # type: ignore
            "expected_ancestors": [(home_page.id, 1), (cat_page.id, 0)],
        },
    ],
)
async def test_page_add(params: Any, sqla_session: AsyncSession, pages: Sequence[Page]):
    repo = PageSQLRepository(sqla_session)
    await repo.add(params["page"])

    qry = select(orm.pages).filter(orm.pages.c.id == params["page"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    page = resp.first()  # type: ignore
    assert page is not None
    assert page.id == params["page"].id

    qry = (
        select(orm.pages_treepath.c.ancestor_id, orm.pages_treepath.c.length)
        .filter(orm.pages_treepath.c.descendant_id == params["page"].id)
        .order_by(orm.pages_treepath.c.length.desc())
    )

    resp = await sqla_session.execute(qry)  # type: ignore
    assert list(resp) == params["expected_ancestors"]  # type: ignore

    qry = (
        select(orm.pages_treepath.c.descendant_id, orm.pages_treepath.c.length)
        .filter(orm.pages_treepath.c.ancestor_id == params["page"].id)
        .order_by(orm.pages_treepath.c.length)
    )

    resp = await sqla_session.execute(qry)  # type: ignore
    assert list(resp) == [(params["page"].id, 0)]  # type: ignore


@pytest.mark.parametrize(
    "params",
    [
        {
            "page": home_page,
            "update_page": fake_page(
                id=home_page.id,
                type="blog:HomePage",
                slug="home",
                title="new title",
                description="new desc",
                hero_title="my new hero",
            ),
            "pages": [home_page, cat_page],  # type: ignore
            "expected_slug": "home",
            "expected_title": "new title",
            "expected_description": "new desc",
            "expected_body": {"body": [], "hero_title": "my new hero"},
        },
    ],
)
async def test_page_update(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)
    await repo.update(params["update_page"])

    qry = select(orm.pages).filter(orm.pages.c.id == params["page"].id)

    resp = await sqla_session.execute(qry)  # type: ignore
    page: orm.pages = resp.first()  # type: ignore
    assert page.slug == params["expected_slug"]
    assert page.title == params["expected_title"]
    assert page.description == params["expected_description"]
    assert page.body == params["expected_body"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "pages": [home_page, cat_page],  # type: ignore
        },
    ],
)
async def test_page_remove(
    params: Any, sqla_session: AsyncSession, pages: Sequence[Page]
):
    repo = PageSQLRepository(sqla_session)

    resp = await repo.remove(home_page)
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
                fake_header_snippet(slug="snip-this"),
                fake_header_snippet(slug="snip-it"),
                fake_header_snippet(slug="snip-that"),
            ],
        },
    ],
)
async def test_snippet_by_slug(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    rsnippet = await repo.by_slug("snip-it")
    assert rsnippet.is_ok()
    snippet = rsnippet.unwrap()
    assert snippet.id == snippets[1].id

    rsnippet = await repo.by_slug("e404")
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
    assert snippet.slug == snippets[1].slug

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
    assert snippet.slug == params["snippet"].slug
    assert snippet.body == {
        "title": params["snippet"].title,
        "links": params["snippet"].links,
    }


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(slug="snip-this"),
                fake_header_snippet(slug="snip-it"),
                fake_header_snippet(slug="snip-that"),
            ],
        },
    ],
)
async def test_snippet_remove(
    params: Any, sqla_session: AsyncSession, snippets: list[Snippet]
):
    repo = SnippetSQLRepository(sqla_session)
    await repo.remove(snippets[1])

    qry = select(orm.snippets).filter(orm.snippets.c.slug == "snip-it")

    resp = await sqla_session.execute(qry)  # type: ignore
    snippet: orm.snippets = resp.first()  # type: ignore
    assert snippet is None

    qry = select(orm.snippets).filter(orm.snippets.c.slug == "snip-that")

    resp = await sqla_session.execute(qry)  # type: ignore
    snippet: orm.snippets = resp.first()  # type: ignore
    assert snippet is not None


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(slug="snip-this"),
                fake_footer_snippet(slug="snip-it"),
                fake_header_snippet(slug="snip-that"),
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
    ss = [s.slug for s in snips]
    assert ss == ["snip-that", "snip-this"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(slug="snip-this"),
                fake_header_snippet(slug="snip-it"),
                fake_header_snippet(slug="snip-that"),
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
    ss = [s.slug for s in snips]
    assert ss == ["snip-it", "snip-that", "snip-this"]


@pytest.mark.parametrize(
    "params",
    [
        {
            "snippets": [
                fake_header_snippet(slug="snip-this"),
                fake_header_snippet(slug="snip-it"),
                fake_header_snippet(slug="snip-that"),
            ],
        },
    ],
)
async def test_snippet_update(
    params: Any, sqla_session: AsyncSession, snippets: list[HeaderSnippet]
):
    snippet = snippets[1]
    snippet.slug = "new-snip-slug"
    snippet.title = "New title"
    snippet.links = [Link(title="l1", href="/l1")]
    repo = SnippetSQLRepository(sqla_session)
    op = await repo.update(snippet)
    assert op.is_ok()

    qry = select(orm.snippets).filter(orm.snippets.c.id == snippet.id)

    resp = await sqla_session.execute(qry)  # type: ignore
    rsnip: orm.snippets = resp.first()  # type: ignore
    assert rsnip.slug == "new-snip-slug"
    assert rsnip.body["title"] == "New title"
    assert rsnip.body["links"] == [{"title": "l1", "href": "/l1"}]


@pytest.mark.parametrize(
    "params",
    [
        {
            "pages": [home_page],
            "site": fake_site(home_page),
        },
    ],
)
async def test_site_add(params: Any, sqla_session: AsyncSession, pages: Sequence[Page]):
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
            "pages": [home_page, cat_page, cat2_page],
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
    pages: Sequence[Page],
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
            "pages": [home_page, cat_page, cat2_page],
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
    pages: Sequence[Page],
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
            "pages": [home_page, cat_page, cat2_page],
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
    pages: Sequence[Page],
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
            "pages": [home_page, cat_page, cat2_page],
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
    pages: Sequence[Page],
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
    assert updated_site.page_id == home_page.id

    qry = select(orm.sites).filter(orm.sites.c.id == sites[0].id)
    resp = await sqla_session.execute(qry)  # type: ignore
    not_updated_site: orm.sites = resp.first()  # type: ignore
    assert not_updated_site.hostname == "www1"
    assert not_updated_site.page_id == cat_page.id

    site.root_page_path = "/e404"
    rsite = await repo.update(site)
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "root_page_not_found"

    site = Site(
        id=generate_id(),
        page_id=None,
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
            "pages": [home_page, cat_page, cat2_page],
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
    pages: Sequence[Page],
    sites: Sequence[Site],
):
    repo = SiteSQLRepository(sqla_session)
    rsite = await repo.by_hostname("www1")

    await repo.remove(rsite.unwrap())

    rsite = await repo.by_hostname("www1")
    assert rsite.is_err()
    site_err = rsite.unwrap_err()
    assert site_err.name == "site_not_found"


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
async def test_sql_uow(params: Any, sql_uow: SQLUnitOfWork, accounts_uow: NoneType):
    async with sql_uow as uow:
        alice_from_uow = await uow.accounts.by_username("alice")
        await uow.rollback()

    assert alice_from_uow.unwrap().id == alice.id
