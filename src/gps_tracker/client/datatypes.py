"""Data-types returned by Invoxia API."""
# pylint: disable=too-few-public-methods
# This file only defines attrs dataclasses which do not
# have to satisfy the minimum public-method count.

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Type

from .exceptions import UnknownDeviceType

try:
    import attrs
except ModuleNotFoundError:
    # Handle attrs<21.3.0
    import attr as attrs  # type: ignore[no-redef]


def _date_converter(val: Optional[str]) -> Optional[datetime]:
    """Converts a datetime in RFC3339 format to datetime object."""
    if val is None:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        # Error will be raised if value does not match format
        # This mainly happens if date does not contain UTC offset
        return datetime.strptime(f"{val}Z", "%Y-%m-%dT%H:%M:%S.%f%z")


def _date_repr(val: Optional[datetime]) -> str:
    """Print a datetime in a compact format."""
    if val is None:
        return str(val)
    return val.isoformat()


@attrs.define(auto_attribs=True)
class User:
    """User definition as returned by Invoxia API."""

    id: int = attrs.field(converter=int)
    """User unique identifier."""

    username: str = attrs.field(converter=str)
    """User name."""

    profiles: List[int] = attrs.field(converter=lambda l: [int(i) for i in l])
    """List of profile ids associated to user."""


@attrs.define(auto_attribs=False)
class Device:
    """Base class for devices."""

    _registry: Dict[str, Type[Device]] = {}

    id: int = attrs.field(converter=int)
    """Device unique identifier."""

    created: datetime = attrs.field(converter=_date_converter, repr=_date_repr)
    """Datetime of device registration."""

    name: str = attrs.field(converter=str)
    """Device name."""

    timezone: str = attrs.field(converter=str)
    """Timezone associated to device."""

    version: str = attrs.field(converter=str)
    """Device version."""

    def __init_subclass__(cls, dtype: Optional[str] = None):
        """Register subclasses with their given type."""
        if dtype is not None:
            Device._registry[dtype] = cls

    @staticmethod
    def get(device_data: dict[str, Any]) -> Device:
        """Generate a Device object based on its type."""
        if device_data["type"] not in Device._registry:
            raise UnknownDeviceType(device_data)

        return Device._registry[device_data.pop("type")](**device_data)

    @classmethod
    def get_types(cls) -> Iterable[str]:
        """Return list of registered device types."""
        return cls._registry.keys()


@attrs.define(slots=False)
class Android(Device, dtype="android"):
    """Definition of devices of type 'android'."""

    serial: uuid.UUID = attrs.field(converter=uuid.UUID)
    """Device Universally Unique Identifier"""


@attrs.define(slots=False)
class Iphone(Device, dtype="iphone"):
    """Definition of devices of type 'iphone'."""

    serial: uuid.UUID = attrs.field(converter=uuid.UUID)
    """Device Universally Unique Identifier"""


class TrackerIcon(enum.Enum):
    """Enumeration of tracker icons."""

    OTHER = 0  # 33
    HANDBAG = 1  # 1
    BRIEFCASE = 2  # 2
    SUITCASE = 3  # 3
    BACKPACK = 5  # 5
    BIKE = 7  # 7
    BOAT = 8  # 8
    CAR = 10  # 10
    CARAVAN = 12
    CART = 13
    KAYAK = 15
    LAPTOP = 16
    MOTO = 17
    HELICOPTER = 18
    PLANE = 19
    SCOOTER = 21
    TENT = 23
    TRUCK = 24
    TRACTOR = 26
    DOG = 30
    CAT = 31  # 31
    PERSON = 32
    GIRL = 34
    BACKHOE_LOADER = 36
    ANIMAL = 37
    WOMAN = 38
    MAN = 39
    EBIKE = 40  # 40
    BEEHIVE = 41  # 41
    CARPARK = 42
    ANTENNA = 43
    HEALTH = 44
    KEYS = 46
    TV = 47
    PHONE = 48  # 48


class TrackerMode(enum.Enum):
    """Enumeration of possible tracker modes."""

    DAILY = 1
    INTENSE = 2
    CHILD = 3
    KEEP_ALIVE = 4
    AIRPLANE = 6
    LOST = 7
    VEHICLE_S1 = 8
    VEHICLE_S2 = 9
    VEHICLE_S3 = 10
    DAILY_PET = 21
    INTENSE_PET = 22
    CHILD_PET = 23
    LOST_PET_DEBUG = 24
    LOST_PET = 27
    LWT3 = 235


class TrackerUsage(enum.Enum):
    """Enumeration of possible tracker usages."""

    BIKE = "bike"
    CAT = "cat"
    CHILD = "child"
    DOG = "dog"
    MOTO = "moto"
    OTHER = "other"
    PERSON = "person"
    PET = "pet"
    TOOL = "tool"
    UND = ""  # Undefined
    VEHICLE = "vehicle"


@attrs.define(auto_attribs=True)
class TrackerConfig:
    """Definition of tracker config data."""

    board_name: str = attrs.field(converter=str)
    """Tracker board-model reference."""

    color: int = attrs.field(converter=int)
    """Icon color."""

    firmware_path: str = attrs.field(converter=str)
    """URL to firmware update (To be confirmed)."""

    icon: TrackerIcon = attrs.field(converter=TrackerIcon)
    """ID of the icon selected for this tracker."""

    mode: TrackerMode = attrs.field(converter=lambda val: TrackerMode(int(val)))
    """Operating mode of the tracker."""

    network: str = attrs.field(converter=str)
    """Network used by tracker (LoRa/SigFox)."""

    network_config: int = attrs.field(converter=int)
    """To be determined."""

    network_region: str = attrs.field(converter=str)
    """Region configured for the network (To be confirmed)."""

    notify_position: bool = attrs.field(converter=bool)
    """Whether notifications must be send when tracker position changes."""

    notify_long_walk: bool = attrs.field(converter=bool)
    """To be determined. Probably related to pet mode."""

    usage: TrackerUsage = attrs.field(converter=TrackerUsage)
    """Tracker usage defined during device setup."""

    image: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
        default=None,
    )
    """Image reference when icon as been replaced by a user-defined image."""

    weight: Optional[float] = attrs.field(
        converter=attrs.converters.optional(float),
        validator=attrs.validators.optional(attrs.validators.instance_of(float)),
        default=None,
    )
    """To be determined. Probably weight of object to which tracker is attached."""


@attrs.define(auto_attribs=True)
class TrackerStatus:
    """Definition of tracker status data."""

    battery: int = attrs.field(converter=int)
    begin_date: datetime = attrs.field(converter=_date_converter, repr=_date_repr)
    network_operator: str = attrs.field(converter=str)
    state: str = attrs.field(converter=str)
    stationary: int = attrs.field(converter=int)
    sub_end_date: str = attrs.field(converter=str)
    sub_state: str = attrs.field(converter=str)
    last_event: Optional[datetime] = attrs.field(
        converter=_date_converter,
        validator=attrs.validators.optional(attrs.validators.instance_of(datetime)),
        default=None,
        repr=_date_repr,
    )
    last_location: Optional[datetime] = attrs.field(
        converter=_date_converter,
        validator=attrs.validators.optional(attrs.validators.instance_of(datetime)),
        default=None,
        repr=_date_repr,
    )


class TrackerMethod(enum.Enum):
    """Enumeration of tracking methods."""

    UNKNOWN = 0
    NETWORK = 1
    GPS = 2
    BSSID = 3
    PLACE = 4
    UBISCALE = 5
    PHONE = 6
    BSSID_TGU = 7
    SERVER = 8
    BSSID2 = 9
    BSSID3 = 10
    BSSID4 = 11
    FLEET_CORRECTION = 12
    BLE_NEIGHBOR = 13
    GPS_BLE = 14
    PHONE2 = 15


@attrs.define(auto_attribs=True)
class TrackerData:
    """Definition of tracker location data."""

    datetime: datetime = attrs.field(converter=_date_converter, repr=_date_repr)
    """Datetime of location measurement."""

    lat: float = attrs.field(converter=float)
    """Device latitude."""

    lng: float = attrs.field(converter=float)
    """Device longitude."""

    method: TrackerMethod = attrs.field(converter=TrackerMethod)
    """Method used for location acquisition."""

    pkt_drop: int = attrs.field(converter=int)
    """To be determined. (Probably number of packet drop since last location)."""

    precision: int = attrs.field(converter=int)
    """Precision of location measurement (To be confirmed)."""

    uuid: uuid.UUID = attrs.field(converter=uuid.UUID)
    """Universally unique identifier of location data."""


def _tracker_config_converter(val: Dict[str, Any]) -> TrackerConfig:
    """Converter to form a TrackerConfig from its JSON representation."""
    return TrackerConfig(**val)


def _tracker_status_converter(val: Dict[str, Any]) -> TrackerStatus:
    """Converter to form a TrackerStatus from its JSON representation."""
    return TrackerStatus(**val)


class Tracker(Device, dtype="tracker"):
    """Base class for trackers."""


@attrs.define(slots=False)
class Tracker01(Tracker, dtype="tracker_01"):
    """Definition of devices of type 'tracker_01'."""

    serial: str = attrs.field(converter=str)
    """Tracker serial number."""

    version_build: str = attrs.field(converter=str)
    """Firmware build reference (To be confirmed)."""

    tracker_config: TrackerConfig = attrs.field(converter=_tracker_config_converter)
    """Tracker configuration data."""

    tracker_status: TrackerStatus = attrs.field(converter=_tracker_status_converter)
    """Tracker current status."""

    model: Optional[str] = attrs.field(
        validator=attrs.validators.optional(attrs.validators.instance_of(str)),
        default=None,
    )
    """Tracker model."""
