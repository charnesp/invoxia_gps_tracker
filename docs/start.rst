.. _start:

Getting Started
===============

Installing gps_tracker
**********************

``gps_tracker`` requires Python 3.9 or later to run. Once you have
set-up your Python environment, simply install ``gps_tracker`` using :code:`pip`:

.. code-block:: shell

    $ pip install gps_tracker


Configure a client
******************

The ``gps_tracker`` client only needs the credentials to your Invoxia™
account to work. You may pass them as following:

.. code-block:: python

    import gps_tracker

    cfg = gps_tracker.Config(username="myusername", password="mypassword")
    client = gps_tracker.Client(cfg)



Access devices and their location data
**************************************

Once the client is configured, accessing your devices is straightforward:

.. code-block:: python

    devices: List[gps_tracker.Device] = client.get_devices()

Note that, by default, all devices associated to your account are returned.
This includes the smartphones (Android or iOS) that were connected through the Invoxia™ app.

To only retrieve trackers, you may filter the query:

.. code-block:: python

    trackers: List[gps_tracker.Tracker] = client.get_devices(kind="tracker")

See the :doc:`Module Reference <api/modules>` for details regarding attributes
of :class:`Android <gps_tracker.client.datatypes.Android>`, :class:`iPhone <gps_tracker.client.datatypes.Iphone>`
and :class:`Tracker <gps_tracker.client.datatypes.Tracker01>` devices.

Once you have an instance of the tracker device you are interested in, you may
query its locations with:

.. code-block:: python

    for tracker in trackers:
        locations: List[gps_tracker.TrackerData] = client.get_locations(tracker)


The :meth:`get_locations <gps_tracker.client.sync.SyncClient.get_locations>` method lets you
define a max count of tracking point to extract and a time period. See its documentation
for more details.

Each :class:`location <gps_tracker.client.datatypes.TrackerData>` contains:

- its date and time;
- its latitude and longitude;
- its acquisition method;
- its precision.
