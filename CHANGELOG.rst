=========
Changelog
=========

0.4.0
-----
- Fix attrs import when attrs<2021.3.0 is installed (required
  for Home-Assistant 2021.12 which pins attrs==2021.2.0)
- Add new client methods: ``get_trackers``, ``get_tracker_config`` and
  ``get_tracker_status``
- Improve synchronous client performances by using a single requests.Session
  over the client lifecycle
- Increase test coverage

0.3.0
-----

- Rename package from ``invoxia`` to ``gps_tracker``

0.2.0
-----

- Implement Asynchronous client using aiohttp

0.1.3
-----

- Fix issues with unit-test execution

0.1.2
-----

- Implement unit-tests for synchronous client

0.1.1
-----

- Fix badges in README.rst

0.1.0
-----

- Implement the synchronous :class:`Client <gps_tracker.client.sync.Client>`
- Document the use of :doc:`current module <api/modules>` and :doc:`quickstart <start>`
- Add :mod:`enumerations <gps_tracker.client.datatypes>` to improve readability
  of some tracker attributes.
