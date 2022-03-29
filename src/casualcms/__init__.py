from pkg_resources import get_distribution

__version__: str = get_distribution("casualcms").version


__all__ = ["__version__"]
