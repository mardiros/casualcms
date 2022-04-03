from datetime import datetime, timedelta
from typing import Any

import pytest

from casualcms.api.domain.model import Account, AuthnToken


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


@pytest.mark.parametrize(
    "params",
    [{"timedelta": 15, "expected": False}, {"timedelta": -15, "expected": True}],
)
def test_authn_token_has_expired(params: dict[str, Any]):
    tok = AuthnToken(
        id="",
        account_id="",
        created_at=datetime.utcnow(),
        token="",
        expires_at=datetime.utcnow() + timedelta(seconds=params["timedelta"]),
        client_addr="",
        user_agent="",
    )
    assert tok.has_expired() == params["expected"]
