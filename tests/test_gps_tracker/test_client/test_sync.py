"""Test synchronous client."""

from datetime import datetime
from typing import List

import pytest

from gps_tracker.client.config import Config
from gps_tracker.client.datatypes import Device, User
from gps_tracker.client.synchronous import Client


def test_client_init():
    """Test instantiation of synchronous client."""
    cfg = Config("", "")
    print(cfg)
    Client(cfg)


def test_get_users(config_authenticated: Config):
    """Test user getters."""

    client = Client(config_authenticated)

    users: List[User] = client.get_users()

    for user in users:
        client.get_user(user.id)


def test_get_devices(config_authenticated):
    """Test devices getters."""

    client = Client(config_authenticated)

    devices: List[Device] = client.get_devices()

    for device in devices:
        client.get_device(device.id)

    for kind in Device.get_types():
        client.get_devices(kind=kind)

    with pytest.raises(KeyError):
        client.get_devices(kind="undefined_kind")


def test_get_locations(config_authenticated):
    """Test getting tracker locations."""

    client = Client(config_authenticated)

    trackers = client.get_devices(kind="tracker")
    tracker = trackers[0]

    locations = client.get_locations(
        tracker,
        not_before=datetime(2004, 11, 4),
        not_after=datetime(2017, 3, 3),
        max_count=21,
    )

    assert len(locations) <= 21

    client.get_locations(tracker)
