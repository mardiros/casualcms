import pkg_resources
from jinja2 import Environment, FileSystemLoader, Template

from casualcms.config import Settings


def build_searchpath() -> list[str]:
    searchpath: list[str] = []
    settings = Settings()
    paths = settings.template_search_path.split(",")
    for path in paths:
        if ":" in path:
            searchpath.append(pkg_resources.resource_filename(*path.split(":", 2)))
        else:
            searchpath.append(path)
    return searchpath


def get_template(template: str) -> Template:
    env = Environment(loader=FileSystemLoader(build_searchpath()))
    return env.get_template(template)
