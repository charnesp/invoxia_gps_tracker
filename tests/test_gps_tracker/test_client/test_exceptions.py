"""Test exceptions are raised as expected."""

import uuid

import pytest

from gps_tracker.client.datatypes import Device
from gps_tracker.client.exceptions import (
    HttpException,
    UnauthorizedQuery,
    UnknownDeviceType,
)


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
    """Test exception instantiation with no message."""

    UnauthorizedQuery()
