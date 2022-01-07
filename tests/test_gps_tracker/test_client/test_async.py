"""Test asynchronous client."""
import asyncio
import datetime
from typing import List
from unittest.mock import patch

import aiohttp
import pytest

import gps_tracker.client.exceptions
from gps_tracker.client.asynchronous import AsyncClient
from gps_tracker.client.datatypes import Device, User
from tests.helpers import AiohttpMock


@pytest.mark.asyncio
async def test_async_context(config_dummy):
    """Test async client with context manager."""
    async with AsyncClient(config_dummy):
        pass


@pytest.mark.asyncio
async def test_get_users(async_client: AsyncClient):
    """Test users getter."""

    with AiohttpMock("200_users.json"):
        users: List[User] = await async_client.get_users()

    assert len(users) == 1
    assert users[0].id == 768046
    assert len(users[0].profiles) == 1


@pytest.mark.asyncio
async def test_get_users_unauthorized(async_client: AsyncClient):
    """Test users getter."""

    with pytest.raises(gps_tracker.client.exceptions.UnauthorizedQuery):
        with AiohttpMock("401_users.json"):
            await async_client.get_users()


@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    """Test user getter with authorized query."""
    user_id = 457961
    with AiohttpMock("200_user_id-457961.json"):
        user: User = await async_client.get_user(user_id=user_id)

    assert user.id == user_id


@pytest.mark.asyncio
async def test_get_user_forbidden(async_client: AsyncClient):
    """Test user getter with forbidden query."""
    user_id = 666666
    with pytest.raises(gps_tracker.client.exceptions.ForbiddenQuery):
        with AiohttpMock("403_user_id-666666.json"):
            await async_client.get_user(user_id=user_id)


@pytest.mark.asyncio
async def test_get_devices(async_client: AsyncClient):
    """Test devices getters."""

    with AiohttpMock("200_devices.json"):
        devices: List[Device] = await async_client.get_devices()

    assert len(devices) == 3
    assert devices[0].id == 222000
    assert isinstance(devices[0], gps_tracker.client.datatypes.Android)


@pytest.mark.asyncio
async def test_get_device_id(async_client: AsyncClient):
    """Test devices getters with specific id."""

    with AiohttpMock("200_device_deviceid-222000.json"):
        device: Device = await async_client.get_device(device_id=222000)

    assert device.id == 222000
    assert isinstance(device, gps_tracker.client.datatypes.Android)


@pytest.mark.asyncio
async def test_get_devices_type(async_client: AsyncClient):
    """Test devices getters with specific type."""

    with AiohttpMock(
        "200_devices_type-android.json",
        "200_devices_type-iphone.json",
        "200_devices_type-tracker.json",
    ):
        android_devices, iphone_devices, trackers = await asyncio.gather(
            async_client.get_devices(kind="android"),
            async_client.get_devices(kind="iphone"),
            async_client.get_trackers(),
        )

    assert len(android_devices) == 1
    assert android_devices[0].id == 222000
    assert isinstance(android_devices[0], gps_tracker.client.datatypes.Android)

    assert len(iphone_devices) == 1
    assert iphone_devices[0].id == 625235
    assert isinstance(iphone_devices[0], gps_tracker.client.datatypes.Iphone)

    assert len(trackers) == 1
    assert trackers[0].id == 878858

    with pytest.raises(KeyError):
        await async_client.get_devices(kind="undefined_kind")

    with AiohttpMock("204_tracker_status-invalid.json"):
        with pytest.raises(gps_tracker.client.exceptions.NoContentQuery):
            await async_client.get_tracker_status(android_devices[0])


@pytest.mark.asyncio
async def test_get_tracker_data(async_client: AsyncClient):
    """Test getting tracker locations."""

    with AiohttpMock("200_devices_type-tracker.json"):
        trackers = await async_client.get_trackers()

    assert len(trackers) == 1
    assert trackers[0].id == 878858
    assert isinstance(trackers[0], gps_tracker.client.datatypes.Tracker)
    assert isinstance(trackers[0], gps_tracker.client.datatypes.Tracker01)

    tracker = trackers[0]

    with AiohttpMock(
        "200_tracker_data_deviceid-878858.json",
        "200_tracker_data_deviceid-878858.json",
        "200_tracker_data_empty_deviceid-878858.json",
        "200_tracker_status_deviceid-878858.json",
        "200_tracker_config_deviceid-878858.json",
    ):
        loc1, loc2, loc3, tracker_status, tracker_config = await asyncio.gather(
            async_client.get_locations(tracker),
            async_client.get_locations(tracker, max_count=23),
            async_client.get_locations(
                tracker,
                not_before=datetime.datetime.fromtimestamp(1533411925),
                not_after=datetime.datetime.fromtimestamp(1639307604),
            ),
            async_client.get_tracker_status(tracker),
            async_client.get_tracker_config(tracker),
        )

    assert len(loc1) == 20
    assert len(loc2) == 23
    assert len(loc3) == 0
    assert tracker_status.battery == 58
    assert tracker_config.network_region == "MOON"


@pytest.mark.asyncio
async def test_async_client_external_session(config_dummy):
    """Test async client with provided session."""
    auth = AsyncClient.get_auth(config_dummy)
    session = aiohttp.ClientSession(auth=auth)

    async with AsyncClient(config_dummy, session) as client:
        with AiohttpMock("200_devices.json"):
            await client.get_devices()

    await session.close()


@pytest.mark.asyncio
async def test_page_not_found(async_client: AsyncClient):
    """Test querying a not found page."""

    with AiohttpMock("404_test.json"):
        with pytest.raises(gps_tracker.client.exceptions.FailedQuery):
            await async_client._query("https://labs.invoxia.io/test/")

    with AiohttpMock("404_test.json"):
        with (
            pytest.raises(aiohttp.ClientResponseError),
            patch(
                "gps_tracker.client.exceptions.HttpException.get_default",
                return_value=None,
            ),
        ):
            await async_client._query("https://labs.invoxia.io/test/")


@pytest.mark.asyncio
async def test_no_connection(async_client: AsyncClient):
    """Test behaviour with no connection."""

    with AiohttpMock("404_test_except-AsyncClientConnectionError.json"):
        with pytest.raises(gps_tracker.client.exceptions.ApiConnectionError):
            await async_client._query("https://labs.invoxia.io/test/")


@pytest.mark.asyncio
async def test_answer_with_unexpected_field(async_client: AsyncClient):
    """Test behaviour with unhandled field returned by API."""
    with AiohttpMock("200_users_unknown-field.json"):
        users: List[User] = await async_client.get_users()

    assert len(users) == 1
    assert users[0].id == 768046
    assert len(users[0].profiles) == 1


@pytest.mark.asyncio
async def test_answer_with_missing_field(async_client: AsyncClient):
    """Test behaviour with unhandled field returned by API."""
    with pytest.raises(gps_tracker.client.exceptions.UnknownAnswerScheme):
        with AiohttpMock("200_users_missing-field.json"):
            await async_client.get_users()
