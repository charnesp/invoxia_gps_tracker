"""conftest.py for invoxia."""

import asyncio
import os
from distutils.version import LooseVersion

import pytest
from importlib_metadata import metadata

from invoxia.client.asynchronous import AsyncClient
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


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", name="async_client")
async def async_client(config_authenticated: Config):  # pylint: disable=W0621
    """Instantiate an asynchronous client."""
    client = AsyncClient(config_authenticated)
    yield client
    await client.close()
    if LooseVersion(metadata("aiohttp")["Version"]) < LooseVersion("4.0.0"):
        # Up to version 4.0 of aiohttp, a client.close() does not
        # wait for the SSL transport to close.
        # This causes issues with pytest execution where the event_loop is closed
        # between client.close() and the actual connection termination.
        # See https://github.com/aio-libs/aiohttp/issues/1925
        await asyncio.sleep(0.25)
