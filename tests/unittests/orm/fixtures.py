from typing import Any, Dict

from faker import Faker

from casualcms.domain.messages.commands import generate_secret
from casualcms.domain.model import (
    Account,
    AuthnToken,
    DraftPage,
    PublishedPage,
    Site,
    Snippet,
    resolve_page_type,
    resolve_setting_type,
    resolve_snippet_type,
)
from casualcms.domain.model.setting import Setting
from casualcms.utils import generate_id

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


def fake_draft_page(type: str, **kwargs: Any) -> DraftPage[Any]:
    dpage: Dict[str, Any] = {
        "id": fake.uuid4(),
        "created_at": fake.past_datetime(),
        "slug": fake.slug(),
        "title": fake.name(),
        "description": fake.paragraph(nb_sentences=1),
        "parent": None,
    }
    typ = resolve_page_type(type).unwrap()
    dpage.update(kwargs)
    draft: DraftPage[Any] = DraftPage(
        id=dpage.pop("id"),
        created_at=dpage.pop("created_at"),
        page=typ(**dpage),
    )
    return draft


def fake_site(page: DraftPage[Any], **kwargs: Any) -> Site:
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


def fake_snippet(type: str, id: str | None = None, **kwargs: Any) -> Snippet[Any]:
    snippet: Dict[str, Any] = {
        "type": type,
        "key": fake.slug(),
    }

    typ = resolve_snippet_type(type).unwrap()
    snippet.update(kwargs)
    snip: Snippet[Any] = Snippet(
        id=id or generate_id(),
        snippet=typ(**snippet),
    )
    return snip


def fake_header_snippet(**kwargs: Any) -> Snippet[Any]:
    snippet: Dict[str, Any] = {
        "title": fake.name(),
        "links": [{"title": fake.paragraph(nb_sentences=1), "href": fake.url()}],
    }
    snippet.update(kwargs)
    return fake_snippet("blog:HeaderSnippet", **snippet)


def fake_footer_snippet(**kwargs: Any) -> Snippet[Any]:
    snippet: Dict[str, Any] = {
        "links": [{"title": fake.paragraph(nb_sentences=1), "href": fake.url()}],
    }
    snippet.update(kwargs)
    return fake_snippet("tests.casualblog.models:FooterSnippet", **snippet)


def fake_setting(key: str, hostname: str = "www", **kwargs: Any) -> Setting[Any]:
    typ = resolve_setting_type(key)
    stg = typ(**kwargs)
    return Setting(
        id=kwargs.pop("id", fake.uuid4()),
        created_at=fake.past_datetime(),
        hostname=hostname,
        key=key,  # type: ignore
        setting=stg,
    )


def fake_ff_setting(hostname: str = "www", **kwargs: Any) -> Setting[Any]:
    settings = {"use_stuff": True, "use_another_stuff": False}
    settings.update(kwargs)  # type: ignore
    return fake_setting("ff", hostname=hostname, **settings)


def fake_contact_setting(hostname: str = "www", **kwargs: Any) -> Setting[Any]:
    settings = {"email": "bob@alice.net"}
    settings.update(kwargs)  # type: ignore
    return fake_setting("contact", hostname=hostname, **settings)


def fake_page(draft: DraftPage[Any], site: Site) -> PublishedPage[Any]:
    lprefix = len(site.root_page_path)
    path = draft.path[lprefix:]
    path = f"//{site.hostname}{path}"
    return PublishedPage(
        id=fake.uuid4(),
        page=draft.page,
        created_at=fake.past_datetime(),
        draft_id=draft.id,
        site=site,
        path=path,
    )
