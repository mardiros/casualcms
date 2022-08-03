import pytest
from casualcms.adapters.resolver import resolve

from casualcms.domain.model.page import Page


def test_resolve_ok():
    hp = resolve("casualcms.domain.model.page:Page")
    assert hp.is_ok()
    assert hp.unwrap() is Page


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
    assert err.unwrap_err() == f"{mod} is not a valid."
