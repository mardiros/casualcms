from typing import Any, Dict

from faker import Faker

from casualcms.domain.messages.commands import generate_secret
from casualcms.domain.model import Account, AuthnToken, Page
from casualcms.domain.model.site import Site

fake = Faker()


def fake_account(**kwargs: Any) -> Account:
    account = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "username": fake.user_name(),
        "password": "secret",
        "email": fake.email(),
        "lang": "en",
    }
    account.update(kwargs)
    return Account(**account)


def fake_authn_tokens(**kwargs: Any) -> AuthnToken:
    token = {
        "id": fake.uuid4(),
        "token": generate_secret(),
        "created_at": fake.past_datetime(),
        # "account_id": account.id,  FK !
        "expires_at": fake.past_datetime(),
        "username": fake.user_name(),
        "client_addr": "1.2.3.4",
        "user_agent": "Mozilla/5",
    }
    token.update(kwargs)
    return AuthnToken(**token)


def fake_page(type: str, **kwargs: Any) -> Page:
    page: Dict[str, Any] = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "slug": fake.slug(),
        "title": fake.name(),
        "description": fake.paragraph(nb_sentences=1),
        "parent": None,
    }
    from casualcms.domain.model.page import resolve_type

    typ = resolve_type(type)
    page.update(kwargs)
    return typ(**page)


def fake_site(page: Page, **kwargs: Any) -> Site:
    site = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "hostname": fake.domain_name(),
        "default": False,
        "page_id": page.id,
        "root": page.path,
    }
    site.update(kwargs)
    return Site(**site)
