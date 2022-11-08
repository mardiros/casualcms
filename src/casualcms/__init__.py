from pkg_resources import get_distribution

from .domain.model.abstract_page import AbstractPage
from .domain.model.abstract_setting import AbstractSetting
from .domain.model.abstract_snippet import AbstractSnippet

__version__: str = get_distribution("casualcms").version


__all__ = [
    "__version__",
    "AbstractPage",
    "AbstractSetting",
    "AbstractSnippet",
]
