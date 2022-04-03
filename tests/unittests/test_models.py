from datetime import datetime
import pytest

from casualcms.api.domain.models import Account


def test_account_password_match():
    account = Account(
        id="1",
        created_at=datetime.now(),
        username="bob",
        password="alice",
        email="",
        lang="fr",
    )
    assert account.match_password("Alice") is False
    assert account.match_password("alice") is True
