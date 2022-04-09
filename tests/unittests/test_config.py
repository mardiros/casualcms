import os

from casualcms.config import Settings


def test_settings(app_settings: None):
    settings = Settings()  # type:ignore
    assert settings.__config__.env_prefix == "casualcms_"
    assert settings.__config__.case_sensitive is False
    assert settings.template_search_path.endswith(
        f"casualcms{os.sep}tests{os.sep}unittests{os.sep}templates"
    )
