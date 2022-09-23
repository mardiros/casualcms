import pytest

from casualcms.domain.model.snippet import AbstractSnippetError

from ..casualblog.models import AbstractFooterSnippet, HeaderSnippet, Link


def test_snippet_metadata():
    snip = HeaderSnippet(
        id="a",
        key="header",
        title="awesome",
        links=[
            Link(title="dogs", href="/dogs"),
            Link(title="cats", href="/cats"),
        ],
    )
    assert snip.get_template() == "header.jinja2"
    assert snip.__meta__.abstract is False
    assert snip.__meta__.type == "blog:HeaderSnippet"


def test_snippet_abstract_raises():
    with pytest.raises(AbstractSnippetError) as context:
        AbstractFooterSnippet()
    assert str(context.value) == "Snippet AbstractFooterSnippet is abstract"


def test_snippet_get_context():
    snip = HeaderSnippet(
        id="a",
        key="header",
        title="awesome",
        links=[
            Link(title="dogs", href="/dogs"),
            Link(title="cats", href="/cats"),
        ],
    )
    expected_context = {
        "links": [
            {"href": "/dogs", "title": "dogs"},
            {"href": "/cats", "title": "cats"},
        ],
        "meta": {"type": "blog:HeaderSnippet"},
        "key": "header",
        "title": "awesome",
    }
    context = snip.get_context()
    assert context == expected_context
    context = snip.get_data_context()
    assert context == expected_context
