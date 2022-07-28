from typing import Any

from faker import Faker

from casualcms.domain.model import Account

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
