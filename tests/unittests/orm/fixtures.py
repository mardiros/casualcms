from typing import Any, Dict

from faker import Faker

from casualcms.domain.messages.commands import generate_secret
from casualcms.domain.model import (
    Account,
    AuthnToken,
    DraftPage,
    Site,
    Snippet,
    resolve_page_type,
    resolve_setting_type,
    resolve_snippet_type,
)

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
        # "user_id": account.id,  FK !
        "expires_at": fake.past_datetime(),
        "username": fake.user_name(),
        "client_addr": "1.2.3.4",
        "user_agent": "Mozilla/5",
    }
    token.update(kwargs)
    return AuthnToken(**token)


def fake_page(type: str, **kwargs: Any) -> DraftPage:
    page: Dict[str, Any] = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "slug": fake.slug(),
        "title": fake.name(),
        "description": fake.paragraph(nb_sentences=1),
        "parent": None,
    }

    typ = resolve_page_type(type).unwrap()
    page.update(kwargs)
    return typ(**page)


def fake_site(page: DraftPage, **kwargs: Any) -> Site:
    site = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "hostname": fake.domain_name(),
        "default": False,
        "secure": True,
        "draft_id": page.id,
        "root_page_path": page.path,
    }
    site.update(kwargs)
    return Site(**site)


def fake_snippet(type: str, **kwargs: Any) -> Snippet:
    snippet: Dict[str, Any] = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "type": type,
        "slug": fake.slug(),
    }

    typ = resolve_snippet_type(type)
    snippet.update(kwargs)
    return typ(**snippet)


def fake_header_snippet(**kwargs: Any):
    snippet: Dict[str, Any] = {
        "title": fake.name(),
        "links": [{"title": fake.paragraph(nb_sentences=1), "href": fake.url()}],
    }
    snippet.update(kwargs)
    return fake_snippet("blog:HeaderSnippet", **snippet)


def fake_footer_snippet(**kwargs: Any):
    snippet: Dict[str, Any] = {
        "links": [{"title": fake.paragraph(nb_sentences=1), "href": fake.url()}],
    }
    snippet.update(kwargs)
    return fake_snippet("tests.casualblog.models:FooterSnippet", **snippet)


def fake_setting(key: str, hostname: str = "www", **kwargs: Any):
    typ = resolve_setting_type(key)
    return typ(hostname=hostname, **kwargs)


def fake_ff_setting(hostname: str = "www", **kwargs: Any):
    settings = {"use_stuff": True, "use_another_stuff": False}
    settings.update(kwargs)  # type: ignore
    return fake_setting("ff", hostname=hostname, **settings)


def fake_contact_setting(hostname: str = "www", **kwargs: Any):
    settings = {"email": "bob@alice.net"}
    settings.update(kwargs)  # type: ignore
    return fake_setting("contact", hostname=hostname, **settings)
