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
    Config.default_api_url()
    print(cfg)
    Client(cfg)


def test_get_users(sync_client: Client):
    """Test user getters."""

    users: List[User] = sync_client.get_users()

    for user in users:
        sync_client.get_user(user.id)


def test_get_devices(sync_client: Client):
    """Test devices getters."""

    devices: List[Device] = sync_client.get_devices()

    for device in devices:
        sync_client.get_device(device.id)

    for kind in Device.get_types():
        sync_client.get_devices(kind=kind)

    with pytest.raises(KeyError):
        sync_client.get_devices(kind="undefined_kind")


def test_get_tracker_data(sync_client: Client):
    """Test getting tracker locations."""

    trackers = sync_client.get_trackers()
    tracker = trackers[0]

    locations = sync_client.get_locations(
        tracker,
        not_before=datetime(2004, 11, 4),
        not_after=datetime(2017, 3, 3),
        max_count=21,
    )
    assert len(locations) <= 21

    sync_client.get_tracker_config(tracker)
    sync_client.get_tracker_status(tracker)

    locations = sync_client.get_locations(tracker)
    print(locations[0])
