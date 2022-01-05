"""Test exceptions are raised as expected."""

import uuid

import pytest

from gps_tracker.client.config import Config
from gps_tracker.client.datatypes import Device
from gps_tracker.client.exceptions import (
    ForbiddenQuery,
    HttpException,
    NoContentQuery,
    UnauthorizedQuery,
    UnknownDeviceType,
)
from gps_tracker.client.synchronous import Client


def test_unknown_device_type():
    """Test that device creation fails on unknown device types."""

    device_data = {
        "type": "unknown",
        "id": 0,
        "name": "Unknown device",
    }

    with pytest.raises(UnknownDeviceType):
        Device.get(device_data)


def test_known_device_type_android():
    """Test that device creation succeeds for known device types."""

    device_data = {
        "id": 0,
        "name": "Android device",
        "type": "android",
        "serial": str(uuid.uuid4()),
        "created": "2004-11-04T13:37:00.000000Z",
        "timezone": "Asia/Tokyo",
        "version": "0.1.2",
    }

    try:
        Device.get(device_data)
    except UnknownDeviceType:
        pytest.fail("UnknownDeviceType raised unexpectedly.")


def test_known_device_type_iphone():
    """Test that device creation succeeds for known device types."""

    device_data = {
        "id": 0,
        "name": "iPhone device",
        "type": "iphone",
        "serial": str(uuid.uuid4()),
        "created": "2004-11-04T13:37:00.000000Z",
        "timezone": "Asia/Tokyo",
        "version": "0.1.2",
    }

    try:
        Device.get(device_data)
    except UnknownDeviceType:
        pytest.fail("UnknownDeviceType raised unexpectedly.")


def test_unauthorized_query():
    """Check exception raised with incorrect credentials."""

    cfg = Config("", "")
    client = Client(cfg)

    with pytest.raises(UnauthorizedQuery):
        client.get_users()


def test_forbidden_query(sync_client: Client):
    """Check exception raised with forbidden query."""

    with pytest.raises(ForbiddenQuery):
        sync_client.get_user(1)


def test_empty_query(sync_client: Client):
    """Test exception raised with no-content query."""

    android_devices = sync_client.get_devices(kind="android")
    with pytest.raises(NoContentQuery):
        # Instruct mypy to ignore arg-type discrepancy as the
        # type enforcement is here to prevent NoContentQuery
        # from being raised.
        sync_client.get_tracker_status(android_devices[0])  # type: ignore[arg-type]


def test_subclass():
    """Test subclassing HttpException without given code."""

    class TestHttpException(HttpException):  # pylint: disable=W0612
        """Dummy class."""


def test_double_subclass():
    """Test subclassing HttpException twice with the same code."""

    with pytest.raises(Exception):

        class UnauthorizedQueryBis(  # pylint: disable=W0612
            HttpException,
            code=401,
        ):
            """Dummy class."""


def test_instantiate_without_msg():
    """Test exception instantiation wi no message."""

    UnauthorizedQuery()
