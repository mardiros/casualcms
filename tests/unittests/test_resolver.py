import pytest

from casualcms.adapters.resolver import resolve
from casualcms.domain.model import DraftPage


def test_resolve_ok():
    hp = resolve("casualcms.domain.model:DraftPage")
    assert hp.is_ok()
    assert hp.unwrap() is DraftPage


@pytest.mark.parametrize(
    "mod",
    [
        "casualcms:UnexistingStuff",
        "not_an_existing_module:Whatever",
        "syntax.error",
    ],
)
def test_resolve_err(mod: str):
    err = resolve(mod)
    assert err.is_err()
    assert err.unwrap_err() == f"{mod} does not resolve any type."
