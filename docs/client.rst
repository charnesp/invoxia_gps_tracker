.. _client.rst:

Client API (Sync/Async)
=======================

Usage example
-------------

``gps_tracker`` provides both a :class:`Synchronous Client <gps_tracker.client.synchronous.Client>` and
an :class:`Asynchronous Client <gps_tracker.client.asynchronous.AsyncClient>` both implementing
the same methods.

The use of each client is illustrated in the following example:

.. code-block:: python

    from gps_tracker import AsyncClient, Client, Config


    def main(config):
        """Use of synchronous client."""
        client = Client(cfg)

        users = client.get_users()
        return users


    async def async_main(config):
        """Use of asynchronous client."""

        async with AsyncClient(config) as client:
            users = await client.get_users()

        return users


    async def async_main_nocontext(config):
        """Use of async client without context."""
        client = AsyncClient(config)

        users = await client.get_users()

        client.close()
        return users


    if __name__ == "__main__":
        cfg = Config(username="myusername", password="mypassword")

        users_sync = main(cfg)
        users_async1 = await async_main(cfg)
        users_async2 = await async_main_nocontext(cfg)


Asynchronous client: closing the session
----------------------------------------

As illustrated previously, asynchronous clients must be closed either by:

- Using an asynchronous context manager

.. code-block:: python

    async with AsyncClient(config) as client:
        ...  # Use client to retrieve data

- By explicitly calling the :meth:`close() <gps_tracker.client.asynchronous.AsyncClient.close>` method:

.. code-block:: python

    client = AsyncClient(config)

    ...  # use client to retrieve data

    client.close()


Client methods
--------------

Retrieve user details
~~~~~~~~~~~~~~~~~~~~~

Invoxia™ API seems to allow multiple users to be associated to a given account.
All these users can be retrieved by:

.. code-block:: python

    users: List[User] = client.get_users()

Where :class:`User <gps_tracker.client.datatypes.User>` contains

- the user :attr:`id <gps_tracker.client.datatypes.User.id>`,
- its :attr:`username <gps_tracker.client.datatypes.User.username>`
- The list of :attr:`profile ids <gps_tracker.client.datatypes.User.profiles>` associated to user

The notion of profiles seems to be useful only for pro users of Invoxia™ devices and services.
Devices can be associated to theses profiles but for general consumers, only a single profile
is associated to your account, thus making profiles irrelevant.
similarly, you will only have a single :class:`User <gps_tracker.client.datatypes.User>` associated
to your credentials.

A single :class:`User <gps_tracker.client.datatypes.User>` can also be retrieve if its ``id``
is known:

.. code-block:: python

    user: User = client.get_user(user_id)

Retrieve devices
~~~~~~~~~~~~~~~~

Invoxia™ API lets you access the list of devices associated to your account.
These contain not only your trackers, but also the smartphones you installed
the Invoxia™ app on.
To get the list of all your devices, user

.. code-block:: python

    devices: List[Device] = client.get_devices()

Each :class:`Device <gps_tracker.client.datatypes.Device>` defines its

- :attr:`id <gps_tracker.client.datatypes.Device.id>`
- :attr:`name <gps_tracker.client.datatypes.Device.name>`
- :attr:`created <gps_tracker.client.datatypes.Device.created>`: date-time when the
  device was added to your account
- :attr:`timezone <gps_tracker.client.datatypes.Device.timezone>`: timezone associated to
  your device
- :attr:`version <gps_tracker.client.datatypes.Device.version>`: version of the
  smartphone app or of the tracker firmware
- ``serial``: serial number of the device

Moreover, :class:`Device <gps_tracker.client.datatypes.Device>` which are also
:class:`Tracker <gps_tracker.client.datatypes.Tracker>` instances will have following attributes:

* :attr:`tracker_config <gps_tracker.client.datatypes.Tracker01.tracker_config>`: Device configuration
* :attr:`tracker_status <gps_tracker.client.datatypes.TrackerConfig.tracker_status>`: Current device status

You may retrieve only trackers with

.. code-block:: python

    trackers: List[Device] = client.get_devices(kind="tracker")

or with its alias which is typed to return ``List[Tracker]``

.. code-block:: python

    trackers: List[Tracker] = client.get_trackers()

Get tracker location
~~~~~~~~~~~~~~~~~~~~

Once you obtain a :class:`Tracker <gps_tracker.client.datatypes.Tracker>` instance,
you may query its locations with

.. code-block:: python

    locations: List[TrackerData] = client.get_locations(tracker)

You may limit the time-period for which you query locations and/or
the maximum count of locations to return:

.. code-block:: python

    locations: List[TrackerData] = client.get_locations(
        tracker,
        not_before=datetime.datetime(year=2021, month=10, day=8),
        not_after=datetime.datetime(year=2021, month=12, day=31),
        max_count=50,
    )

Note that one API query returns up to 20 locations.
Asking for more than that will thus be slower.

Exceptions
----------

All client methods which interrogate the Invoxia™ API can return any of
the following :mod:`exceptions <gps_tracker.client.exceptions>` which all derive
from the base exception :class:`GpsTrackerException <gps_tracker.client.exceptions.GpsTrackerException>`:

- :class:`ApiConnectionError <gps_tracker.client.exceptions.ApiConnectionError>`:
  Error raised during the connection to the API endpoint (failed DNS lookup, SSL issue,
  internet connection not available, ...).
- :class:`UnknownAnswerScheme <gps_tracker.client.exceptions.UnknownAnswerScheme>`:
  The data returned by the API does not match expected content. Please open an issue
  is you face this exception so that the data scheme can be updated.
- :class:`UnknownDeviceType <gps_tracker.client.exceptions.UnknownDeviceType>`:
  A device of unknown type is linked to your account. Please open an issue if you
  face this exception so that the new kind of device can be supported by ``gps_tracker``.
- :class:`UnauthorizedQuery <gps_tracker.client.exceptions.UnauthorizedQuery>`:
  Your credentials are incorrect.
- :class:`ForbiddenQuery <gps_tracker.client.exceptions.ForbiddenQuery>`:
  You are correctly authenticated but you are requesting data for which you do not
  have the permissions.
- :class:`NoContentQuery <gps_tracker.client.exceptions.NoContentQuery>`:
  The server does not have any data for your request. Happens mainly when asking
  for tracker-specific data on a non-tracker device.
- :class:`FailedQuery <gps_tracker.client.exceptions.FailedQuery>`:
  The server returned an error code which does not correspond to any previous
  exception.
