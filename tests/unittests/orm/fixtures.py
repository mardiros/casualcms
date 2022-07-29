from typing import Any

from faker import Faker
from casualcms.domain.messages.commands import generate_secret

from casualcms.domain.model import Account, AuthnToken

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
