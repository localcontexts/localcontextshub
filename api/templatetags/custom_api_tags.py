import os
from urllib.parse import urlparse
from urllib.parse import urljoin

from django import template


register = template.Library()


@register.simple_tag
def external_api(external_url: str) -> str:
    """
    Tag converts an external_url into an internal_url
    so the response can be mocked with a fixture.

    Args:
        external_url: Url to an external API resource.

    Returns:
        When TEST_LIVE_SERVER_DOMAIN is available, the url is transformed so
        the external domain is swapped with the TEST_LIVE_SERVER_DOMAIN.
    """
    test_live_server_domain = os.environ.get('TEST_LIVE_SERVER_DOMAIN')
    if not test_live_server_domain:
        return external_url
    url_components = urlparse(external_url)

    try:
        # return the internal_url formed by the domain and url_components.path
        return urljoin(test_live_server_domain, url_components.path)
    except Exception:
        return external_url
