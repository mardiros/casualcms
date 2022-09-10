from casualcms.domain.model import Site


def test_page_metadata(default_site: Site):
    assert default_site.url == "http://www.example.net"
