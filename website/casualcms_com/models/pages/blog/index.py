from casualcms.domain.model.abstract_page import AbstractPage


class BlogRootPage(AbstractPage):
    class Meta:
        parent_types = ["HomePage"]
        type = "BlogRootPage"
        template = "blog/index.jinja2"
