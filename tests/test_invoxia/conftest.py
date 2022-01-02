"""conftest.py for invoxia."""

import os

import pytest

from invoxia.client.config import Config


@pytest.fixture(scope="module")
def config_authenticated():
    """Form Config is credential in environment."""
    username = os.getenv("INVOXIA_USERNAME")
    password = os.getenv("INVOXIA_PASSWORD")

    if not username or not password:
        pytest.skip("Credentials not found in environment.")
        return Config("", "")

    return Config(username=username, password=password)
