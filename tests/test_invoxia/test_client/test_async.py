"""Test asynchronous client."""
import asyncio
from datetime import datetime
from typing import List

import pytest

from invoxia.client.asynchronous import AsyncClient
from invoxia.client.datatypes import Device, Tracker, User


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
async def test_get_locations(async_client: AsyncClient):
    """Test getting tracker locations."""

    trackers = await async_client.get_devices(kind="tracker")
    tracker = trackers[0]

    if isinstance(tracker, Tracker):
        locations, _ = await asyncio.gather(
            async_client.get_locations(
                tracker,
                not_before=datetime(2004, 11, 4),
                not_after=datetime(2017, 3, 3),
                max_count=21,
            ),
            async_client.get_locations(tracker),
        )

        assert len(locations) <= 21
