from datetime import datetime, timedelta
from typing import Any

import pytest

from casualcms.domain.model import Account, AuthnToken


def test_account_password_match(admin_account: Account):
    assert admin_account.match_password("SuperSecret") is False
    assert admin_account.match_password("supersecret") is True


@pytest.mark.parametrize(
    "params",
    [{"timedelta": 15, "expected": False}, {"timedelta": -15, "expected": True}],
)
def test_authn_token_has_expired(params: dict[str, Any]):
    tok = AuthnToken(
        id="",
        user_id="",
        created_at=datetime.utcnow(),
        token="",
        expires_at=datetime.utcnow() + timedelta(seconds=params["timedelta"]),
        client_addr="",
        user_agent="",
    )
    assert tok.has_expired() == params["expected"]
