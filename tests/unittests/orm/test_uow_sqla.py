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
)
from casualcms.domain.model.page import Page

from .fixtures import fake_account, fake_authn_tokens, fake_page

alice = fake_account(username="alice")
bob = fake_account(username="bob")
dylan = fake_account(username="dylan")
henry = fake_account(username="henry")


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
    rok = root_page.unwrap_err()
    assert rok.name == "page_not_found"


@pytest.mark.parametrize(
    "params",
    [
        {
            "parent": None,
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["root"],
            "expected_ids": [home_page.id],
        },
        {
            "parent": "/root",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["seo", "tech"],
            "expected_ids": [cat2_page.id, cat_page.id],
        },
        {
            "parent": "/root/tech",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": ["seo"],
            "expected_ids": [blog_page.id],
        },
        {
            "parent": "/root/seo",
            "pages": [home_page, cat_page, cat2_page, blog_page],  # type: ignore
            "expected_slugs": [],
            "expected_ids": [],
        },
    ],
)
async def test_page_add(params: Any, sqla_session: AsyncSession, pages: Sequence[Page]):
    repo = PageSQLRepository(sqla_session)
    child_pages = await repo.by_parent(params["parent"])
    assert child_pages.is_ok()
    ps = child_pages.unwrap()
    assert [p.slug for p in ps] == params["expected_slugs"]


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
            "expected_body": {'body': [], 'hero_title': 'my new hero'},
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
