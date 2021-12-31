"""Definition of exceptions possibly raised by the Client."""

import json
from importlib import metadata
from typing import Any, Dict

_homepage: str = metadata.metadata("invoxia")["Home-page"]


class UnknownDeviceType(Exception):
    """Exception raised when a device of unknown type is found."""

    def __init__(self, device_data: Dict[str, Any]):
        """Store device data in exception."""
        self.device_data = device_data
        super().__init__(
            f"""
Device of type '{device_data["type"]}' are not supported.
Please open an issue at {_homepage} with the following content:
{json.dumps(device_data, indent=4)}
Obfuscate any sensitive data by replacing letters by 'a' and digits by '0' if needed."""
        )
