"""Test synchronous client."""

import datetime
from typing import List
from unittest.mock import patch

import pytest
import requests

import gps_tracker
from gps_tracker.client.config import Config
from gps_tracker.client.datatypes import Device, User
from gps_tracker.client.synchronous import Client
from tests.helpers import RequestsMock


def test_client_init():
    """Test instantiation of synchronous client."""
    cfg = Config("", "")
    Config.default_api_url()
    print(cfg)
    Client(cfg)


def test_get_users(sync_client: Client):
    """Test users getter."""

    with RequestsMock("200_users.json"):
        users: List[User] = sync_client.get_users()

    assert len(users) == 1
    assert users[0].id == 768046
    assert len(users[0].profiles) == 1


def test_get_users_unauthorized(sync_client: Client):
    """Test users getter."""

    with pytest.raises(gps_tracker.client.exceptions.UnauthorizedQuery):
        with RequestsMock("401_users.json"):
            sync_client.get_users()


def test_get_user(sync_client: Client):
    """Test user getter with authorized query."""
    user_id = 457961
    with RequestsMock("200_user_id-457961.json"):
        user: User = sync_client.get_user(user_id=user_id)

    assert user.id == user_id


def test_get_user_forbidden(sync_client: Client):
    """Test user getter with forbidden query."""
    user_id = 666666
    with pytest.raises(gps_tracker.client.exceptions.ForbiddenQuery):
        with RequestsMock("403_user_id-666666.json"):
            sync_client.get_user(user_id=user_id)


def test_get_devices(sync_client: Client):
    """Test devices getters."""

    with RequestsMock("200_devices.json"):
        devices: List[Device] = sync_client.get_devices()

    assert len(devices) == 3
    assert devices[0].id == 222000
    assert isinstance(devices[0], gps_tracker.client.datatypes.Android)


def test_get_device_id(sync_client: Client):
    """Test devices getters with specific id."""

    with RequestsMock("200_device_deviceid-222000.json"):
        device: Device = sync_client.get_device(device_id=222000)

    assert device.id == 222000
    assert isinstance(device, gps_tracker.client.datatypes.Android)


def test_get_devices_type(sync_client: Client):
    """Test devices getters with specific type."""

    with RequestsMock(
        "200_devices_type-android.json",
        "200_devices_type-iphone.json",
        "200_devices_type-tracker.json",
    ):
        android_devices = sync_client.get_devices(kind="android")
        iphone_devices = sync_client.get_devices(kind="iphone")
        trackers = sync_client.get_trackers()

    assert len(android_devices) == 1
    assert android_devices[0].id == 222000
    assert isinstance(android_devices[0], gps_tracker.client.datatypes.Android)

    assert len(iphone_devices) == 1
    assert iphone_devices[0].id == 625235
    assert isinstance(iphone_devices[0], gps_tracker.client.datatypes.Iphone)

    assert len(trackers) == 1
    assert trackers[0].id == 878858

    with pytest.raises(KeyError):
        sync_client.get_devices(kind="undefined_kind")

    with RequestsMock("204_tracker_status-invalid.json"):
        with pytest.raises(gps_tracker.client.exceptions.NoContentQuery):
            sync_client.get_tracker_status(android_devices[0])


def test_get_tracker_data(sync_client: Client):
    """Test getting tracker locations."""

    with RequestsMock("200_devices_type-tracker.json"):
        trackers = sync_client.get_trackers()

    assert len(trackers) == 1
    assert trackers[0].id == 878858
    assert isinstance(trackers[0], gps_tracker.client.datatypes.Tracker)
    assert isinstance(trackers[0], gps_tracker.client.datatypes.Tracker01)

    tracker = trackers[0]

    with RequestsMock(
        "200_tracker_data_deviceid-878858.json",
        "200_tracker_data_deviceid-878858.json",
        "200_tracker_data_empty_deviceid-878858.json",
        "200_tracker_status_deviceid-878858.json",
        "200_tracker_config_deviceid-878858.json",
    ):
        loc1, loc2, loc3, tracker_status, tracker_config = (
            sync_client.get_locations(tracker),
            sync_client.get_locations(tracker, max_count=23),
            sync_client.get_locations(
                tracker,
                not_before=datetime.datetime.fromtimestamp(1533411925),
                not_after=datetime.datetime.fromtimestamp(1639307604),
            ),
            sync_client.get_tracker_status(tracker),
            sync_client.get_tracker_config(tracker),
        )

    repr(tracker_status)
    assert len(loc1) == 20
    assert len(loc2) == 23
    assert len(loc3) == 0
    assert tracker_status.battery == 58
    assert tracker_config.network_region == "MOON"


def test_page_not_found(sync_client: Client):
    """Test querying a not found page."""

    with RequestsMock("404_test.json"):
        with pytest.raises(gps_tracker.client.exceptions.FailedQuery):
            sync_client._query("https://labs.invoxia.io/test/")

    with RequestsMock("404_test.json"):
        with (
            pytest.raises(requests.RequestException),
            patch(
                "gps_tracker.client.exceptions.HttpException.get_default",
                return_value=None,
            ),
        ):
            sync_client._query("https://labs.invoxia.io/test/")


def test_no_connection(sync_client: Client):
    """Test behaviour with no connection."""

    with RequestsMock("404_test_except-SyncClientConnectionError.json"):
        with pytest.raises(gps_tracker.client.exceptions.ApiConnectionError):
            sync_client._query("https://labs.invoxia.io/test/")


def test_answer_with_unexpected_field(sync_client: Client):
    """Test behaviour with unhandled field returned by API."""
    with RequestsMock("200_users_unknown-field.json"):
        users: List[User] = sync_client.get_users()

    assert len(users) == 1
    assert users[0].id == 768046
    assert len(users[0].profiles) == 1


def test_answer_with_missing_field(sync_client: Client):
    """Test behaviour with unhandled field returned by API."""
    with pytest.raises(gps_tracker.client.exceptions.UnknownAnswerScheme):
        with RequestsMock("200_users_missing-field.json"):
            sync_client.get_users()
