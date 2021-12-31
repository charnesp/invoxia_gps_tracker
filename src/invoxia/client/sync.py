"""Synchronous client for Invoxia API."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

import requests

from .datatypes import Device, Tracker, TrackerData, User
from .url_provider import UrlProvider

if TYPE_CHECKING:
    from .config import Config

    JsonValue = Union[Dict[str, Any], List[Any], int, str, float, bool, None]
    JsonDict = Dict[str, JsonValue]
    JsonList = List[JsonDict]


class SyncClient:
    """Synchronous client for Invoxia API."""

    def __init__(self, config: Config):
        """Initialize the Client with given configuration."""
        self._cfg: Config = config

        self._url_provider = UrlProvider(api_url=config.api_url)

    def _query(self, url: str) -> Union[JsonDict, JsonList]:
        """Query the API synchronously and return the decoded JSON response."""

        request = requests.get(url=url, auth=(self._cfg.username, self._cfg.password))
        request.raise_for_status()

        return request.json()

    def _query_list(self, url: str) -> JsonList:
        """Query the API and return a list of JSON objects."""
        result = self._query(url)
        return result if isinstance(result, list) else []

    def _query_dict(self, url: str) -> JsonDict:
        """Query the API and return a list of JSON objects."""
        result = self._query(url)
        return result if isinstance(result, dict) else {}

    def get_user(self, user_id: int) -> User:
        """Return a user referenced by its id."""
        data: JsonDict = self._query_dict(self._url_provider.user(user_id))
        return User(**data)

    def get_users(self) -> List[User]:
        """Return all users associated to credentials."""
        data: JsonList = self._query_list(self._url_provider.users())
        return [User(**item) for item in data]

    def get_device(self, device_id: int) -> Device:
        """Return a device referenced by its id."""

        data: JsonDict = self._query_dict(self._url_provider.device(device_id))
        return Device.get(data)

    def get_devices(self) -> List[Device]:
        """Return all devices associated to credentials."""
        data: JsonList = self._query_list(self._url_provider.devices())
        return [Device.get(item) for item in data]

    def get_locations(
        self,
        device: Tracker,
        not_before: Optional[datetime.datetime] = None,
        not_after: Optional[datetime.datetime] = None,
        max_count: int = 50,
    ) -> List[TrackerData]:
        """Extract the list of tracker locations."""
        not_before_ts: Optional[int] = (
            None if not_before is None else not_before.timestamp().__ceil__()
        )

        not_after_ts: Optional[int] = (
            None if not_after is None else not_after.timestamp().__floor__()
        )

        res = []
        while max_count > 0:
            data: JsonList = self._query_list(
                self._url_provider.locations(
                    device_id=device.id,
                    not_after=not_after_ts,
                    not_before=not_before_ts,
                )
            )  # Seems to return between 0 and 20 locations.

            # Stop if not result returned.
            if len(data) == 0:
                break

            # Pop returned results one by one and stop if max_count is reached.
            while len(data) > 0:
                res.append(TrackerData(**data.pop(0)))
                max_count -= 1
                if max_count <= 0:
                    break

            # Update not_after to match the currently oldest location.
            not_after_ts = res[-1].datetime.timestamp().__floor__()

        return res
