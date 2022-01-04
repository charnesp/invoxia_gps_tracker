"""Test exceptions are raised as expected."""

import uuid

import pytest

from gps_tracker.client.config import Config
from gps_tracker.client.datatypes import Device
from gps_tracker.client.exceptions import (
    ForbiddenQuery,
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


def test_forbidden_query(config_authenticated: Config):
    """Check exception raised with forbidden query."""

    client = Client(config_authenticated)

    with pytest.raises(ForbiddenQuery):
        client.get_user(1)
