.. _start:

Getting Started
===============

Installing invoxia
******************

:code:`invoxia` requires Python 3.9 or later to run. Once you have
set-up your Python environment, simply install :code:`invoxia` using :code:`pip`:

.. code-block:: shell

    $ pip install invoxia


Configure a client
******************

The invoxia client only needs your credentials to work.
You may pass them as following:

.. code-block:: python

    import invoxia

    cfg = invoxia.Config(username="myusername",
                         password="mypassword")
    client = invoxia.Client(cfg)



Access devices and their location data
**************************************

Once the client is configured, accessing your devices is straightforward:

.. code-block:: python

    devices: List[invoxia.Device] = client.get_devices()

Note that, by default, all devices associated to your account are returned.
This includes the smartphones (Android or iOS) that were connected through the Invoxia App.

To only retrieve trackers, you may filter the query:

.. code-block:: python

    trackers: List[invoxia.Tracker] = client.get_devices(kind='tracker')

See the :doc:`Module Reference <api/modules>` for details regarding attributes
of :class:`Android <invoxia.client.datatypes.Android>`, :class:`iPhone <invoxia.client.datatypes.Iphone>`
and :class:`Tracker <invoxia.client.datatypes.Tracker01>` devices.

Once you have an instance of the tracker device you are interested in, you may
query its locations with:

.. code-block:: python

    for tracker in trackers:
        locations: List[invoxia.TrackerData] = client.get_locations(tracker)


The :meth:`get_locations <invoxia.client.sync.SyncClient.get_locations>` method lets you
define a max count of tracking point to extract and a time period. See its documentation
for more details.

Each :class:`location <invoxia.client.datatypes.TrackerData>` contains:

- its date and time;
- its latitude and longitude;
- its acquisition method;
- its precision.
