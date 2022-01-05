"""Definition of Client configuration."""

from __future__ import annotations

import urllib.parse

try:
    import attrs
except ModuleNotFoundError:
    # Handle attrs<21.3.0
    import attr as attrs  # type: ignore[no-redef]


def _api_url_converter(val: str) -> str:
    """
    Convert the API URL to expected format.

    Hostname must contain only the connection scheme and FQDN
    without trailing slash.

    :param val: user-defined input value for the API URL
    :type val: str

    :return: properly formatted API URL
    :rtype: str
    """
    val_parsed = urllib.parse.urlparse(val)
    return f"{val_parsed.scheme}://{val_parsed.netloc}"


def _password_repr(val: str) -> str:
    """Change representation of password to hide its content."""
    del val
    return "'********'"


@attrs.define(auto_attribs=True)
class Config:  # pylint: disable=too-few-public-methods
    """Configuration for API Clients."""

    username: str = attrs.field(validator=attrs.validators.instance_of(str))
    """Username used as credentials on Invoxia account."""

    password: str = attrs.field(
        validator=attrs.validators.instance_of(str), repr=_password_repr
    )
    """Password used as credentials on Invoxia account."""

    api_url: str = attrs.field(
        converter=_api_url_converter, default="https://labs.invoxia.io"
    )
    """Invoxia API URL."""

    @classmethod
    def default_api_url(cls) -> str:
        """Return the default API URL."""
        return attrs.fields(cls).api_url.default
