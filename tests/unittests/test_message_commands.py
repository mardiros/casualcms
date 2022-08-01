from casualcms.domain.messages.commands import generate_secret


def test_generate_secret():
    assert len(generate_secret()) == 86
