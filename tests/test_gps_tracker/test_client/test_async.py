"""Test asynchronous client."""
import asyncio
from datetime import datetime
from typing import List

import pytest

from gps_tracker.client.asynchronous import AsyncClient
from gps_tracker.client.datatypes import Device, User


@pytest.mark.asyncio
async def test_async_context(config_authenticated):
    """Test async client with context manager."""
    async with AsyncClient(config_authenticated):
        pass


@pytest.mark.asyncio
async def test_get_users(async_client: AsyncClient):
    """Test user getters."""

    users: List[User] = await async_client.get_users()

    await asyncio.gather(*[async_client.get_user(user.id) for user in users])


@pytest.mark.asyncio
async def test_get_devices(async_client: AsyncClient):
    """Test devices getters."""

    devices: List[Device] = await async_client.get_devices()

    await (
        asyncio.gather(
            *[async_client.get_device(device.id) for device in devices],
            *[async_client.get_devices(kind=kind) for kind in Device.get_types()]
        )
    )

    with pytest.raises(KeyError):
        await async_client.get_devices(kind="undefined_kind")


@pytest.mark.asyncio
async def test_get_tracker_data(async_client: AsyncClient):
    """Test getting tracker locations."""

    trackers = await async_client.get_trackers()
    tracker = trackers[0]

    results = await asyncio.gather(
        async_client.get_locations(
            tracker,
            not_before=datetime(2004, 11, 4),
            not_after=datetime(2017, 3, 3),
            max_count=21,
        ),
        async_client.get_locations(tracker),
        async_client.get_tracker_config(tracker),
        async_client.get_tracker_status(tracker),
    )

    assert len(results[0]) <= 21
