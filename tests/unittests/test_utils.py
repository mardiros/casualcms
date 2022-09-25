from uuid import UUID

import pytest

from casualcms.utils import generate_id, generate_secret


def test_generate_id():
    id_generated = generate_id()
    try:
        assert UUID(id_generated)
    except ValueError:
        pytest.fail("Not a valid uuid")


def test_generate_secret():
    assert len(generate_secret()) == 86
