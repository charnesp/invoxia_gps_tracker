"""Asynchronous client for Invoxia API."""
# pylint: disable=R0801  # Code duplicated with sync client

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, List, Optional

import aiohttp

from .datatypes import Device, Tracker, TrackerConfig, TrackerData, TrackerStatus, User
from .exceptions import HttpException
from .url_provider import UrlProvider

if TYPE_CHECKING:
    from .config import Config


class AsyncClient:
    """Asynchronous client for Invoxia API."""

    def __init__(self, config: Config):
        """Initialize the Client with given configuration."""
        self._cfg: Config = config

        self._url_provider = UrlProvider(api_url=config.api_url)

        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Enter context manager"""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        await self.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Open the session if needed and return it."""
        if self._session is None:
            auth = aiohttp.BasicAuth(
                login=self._cfg.username, password=self._cfg.password
            )
            self._session = aiohttp.ClientSession(auth=auth)
        return self._session

    async def _query(self, url: str) -> Any:
        """Query the API asynchronously and return the decoded JSON response."""

        # Run the request
        session = await self._get_session()
        async with session.get(url) as resp:
            # Extract JSON answer if possible
            json_answer = None
            try:
                json_answer = await resp.json()
            except aiohttp.ContentTypeError:
                pass

            # Raise known exception if required
            exception = HttpException.get(resp.status)
            if exception is not None:
                raise exception(json_answer=json_answer)

            # Raise unknown exception if required
            resp.raise_for_status()

            return json_answer

    async def close(self):
        """Close current session."""
        if self._session is not None:
            await self._session.close()

    async def get_user(self, user_id: int) -> User:
        """
        Return a user referenced by its id.

        :param user_id: ID of the user to retrieve
        :type user_id: int

        :return: User instance associated to given ID
        :rtype: User

        :raise UnauthorizedQuery: Credentials are invalid
        :raise ForbiddenQuery: User of given ID is not linked to
            current account
        :raise aiohttp.ClientResponseError: Unexpected HTTP error
            during API call
        """
        data = await self._query(self._url_provider.user(user_id))
        return User(**data)

    async def get_users(self) -> List[User]:
        """
        Return all users associated to credentials.

        The API definition seems to indicate that multiple users
        can be associated to a single account (probably for pro subscriptions).
        For public consumers, this methods will return a single user.

        :return: List of User instances associated to account
        :rtype: List[User]

        :raise UnauthorizedQuery: Credentials are invalid
        :raise aiohttp.ClientResponseError: Unexpected HTTP error
            during API call
        """
        data = await self._query(self._url_provider.users())
        return [User(**item) for item in data]

    async def get_device(self, device_id: int) -> Device:
        """
        Return a device referenced by its id.

        :param device_id: Unique identifier of a device
        :type device_id: int

        :return: Device instance of given id
        :rtype: Device

        :raise UnauthorizedQuery: Credentials are invalid
        :raise ForbiddenQuery: Device of given ID is not linked to
            current account
        :raise aiohttp.ClientResponseError: Unexpected HTTP error
            during API call
        """

        data = await self._query(self._url_provider.device(device_id))
        return Device.get(data)

    async def get_devices(self, kind: Optional[str] = None) -> List[Device]:
        """
        Return devices associated to credentials.

        By default, all devices (included associated smartphones) are
        returned. The `kind` parameter allows to filter only
        devices of a given type ('android', 'iphone' or 'tracker').

        :param kind: kind of devices to retrieve
        :type kind: str, optional

        :return: List of retrieved devices
        :rtype: List[Device]

        :raise UnauthorizedQuery: Credentials are invalid
        :raise aiohttp.ClientResponseError: Unexpected HTTP error
            during API call
        :raise KeyError: Undefined kind requested
        """
        data = await self._query(self._url_provider.devices(kind=kind))
        return [Device.get(item) for item in data]

    async def get_trackers(self) -> List[Tracker]:
        """
        Query API for the list of trackers associated to credentials.

        :return: Tracker devices associated to current account
        :rtype: List[Tracker]

        :raise UnauthorizedQuery: Credentials are invalid
        :raise requests.HTTPError: Unexpected HTTP error during API call
        """
        data = await self._query(self._url_provider.devices(kind="tracker"))
        trackers: List[Tracker] = []
        for item in data:
            device = Device.get(item)
            if isinstance(device, Tracker):
                trackers.append(device)
        return trackers

    async def get_locations(
        self,
        device: Tracker,
        not_before: Optional[datetime.datetime] = None,
        not_after: Optional[datetime.datetime] = None,
        max_count: int = 20,
    ) -> List[TrackerData]:
        """
        Extract the list of tracker locations.

        :param device: The tracker instance whose locations must be extracted.
        :type device: Tracker

        :param not_before: Minimum date-time of the locations to extract.
        :type not_before: datetime.datetime, optional

        :param not_after: Maximum date-time of the locations to extract.
        :type not_after: datetime.datetime, optional

        :param max_count: Maximum count of position to extract. Note that
            one API query yields 20 locations.
        :type max_count: int, optional

        :return: List of extracted locations
        :rtype: List[TrackerData]

        :raise UnauthorizedQuery: Credentials are invalid
        :raise ForbiddenQuery: provided Device is not linked to
            current account (should not happen if Device was obtained
            with :meth:`get_devices`).
        :raise aiohttp.ClientResponseError: Unexpected HTTP error
            during API call
        """
        not_before_ts: Optional[int] = (
            None if not_before is None else not_before.timestamp().__ceil__()
        )

        not_after_ts: Optional[int] = (
            None if not_after is None else not_after.timestamp().__floor__()
        )

        res = []
        while max_count > 0:
            data = await self._query(
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

    async def get_tracker_status(self, device: Tracker) -> TrackerStatus:
        """
        Get the current status of a given tracker.

        :param device: The tracker instance whose status is queried.
        :type device: Tracker

        :return: Current status of the tracker
        :rtype: TrackerStatus
        """
        data = await self._query(self._url_provider.tracker_status(device_id=device.id))
        return TrackerStatus(**data)

    async def get_tracker_config(self, device: Tracker) -> TrackerConfig:
        """
        Get the current configuration of a given tracker.

        :param device: The tracker instance whose configuration is queried.
        :type device: Tracker

        :return: Current config of the tracker
        :rtype: TrackerConfig
        """
        data = await self._query(self._url_provider.tracker_config(device_id=device.id))
        return TrackerConfig(**data)
