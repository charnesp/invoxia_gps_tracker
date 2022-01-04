.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/
.. image:: https://gitlab.com/ezlo.picori/gps_tracker/badges/main/pipeline.svg
    :alt: Pipeline status
    :target: https://gitlab.com/ezlo.picori/gps_tracker/-/commits/main
.. image:: https://gitlab.com/ezlo.picori/gps_tracker/badges/main/coverage.svg
    :alt: Coverage
    :target: https://gitlab.com/ezlo.picori/gps_tracker/-/commits/main
.. image:: https://readthedocs.org/projects/gps_tracker/badge/?version=latest
    :alt: ReadTheDocs
    :target: https://gps_tracker.readthedocs.io/en/stable/
.. image:: https://img.shields.io/pypi/v/gps_tracker.svg
    :alt: PyPI-Server
    :target: https://pypi.org/project/gps_tracker/

===========
gps_tracker
===========

    Unofficial client to retrieve location data from Invoxia™ GPS trackers.

Invoxia_\™ is known for their GPS Trackers with long battery life which rely on the LoRa_ or SigFox_
networks. Unfortunately, trackers location can only be accessed through their Android_ and iOS_ applications.
This ``gps_tracker`` package connects to the same API than your smartphone app and gives you an easy access to:

- The list of devices connected to your account
- Their current state
- Their location history

Data is only in read-access, you will still need the smartphone app to change your devices configuration.

Note that even though direct access to Invoxia™ API is not strictly prohibited in their `terms of use`_, it is
not encouraged either: company representatives have already stated that they do not currently consider making the
API opened for all customers and this feature is limited to their `pro tracking offer`_.
Therefore, by using ``gps_tracker`` you:

1. Accept to use this direct API access in a reasonable manner by limiting the query rate to the bare minimum required
for your application.

2. Understand that the Invoxia company may take any action they see fit regarding your account if they consider your
usage of their API to be in violation with their terms of use.

.. _Invoxia: https://www.invoxia.com/
.. _LoRa: https://lora-alliance.org/
.. _SigFox: https://www.sigfox.com/
.. _Android: https://play.google.com/store/apps/details?id=com.invoxia.track
.. _iOS: https://apps.apple.com/fr/app/invoxia-gps/id1261314542
.. _`terms of use`: https://www.invoxia.com/fr/legal/site/terms
.. _pro tracking offer: https://tracking.invoxia.com
