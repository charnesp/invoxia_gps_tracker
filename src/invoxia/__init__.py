"""invoxia sub-package imports and metadata definition."""

from invoxia.client import Client, Config, Device, Tracker, TrackerData

try:
    from invoxia._version import version as ver  # pylint: disable=E0401,E0611

    __version__ = ver
    del ver
except ModuleNotFoundError:
    try:
        from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

        __version__ = version(__name__)
    except PackageNotFoundError:  # pragma: no cover
        __version__ = "unknown"
    finally:
        del version, PackageNotFoundError
