"""Definition of exceptions possibly raised by the Client."""

from __future__ import annotations

import json
from importlib import metadata
from typing import Any, Dict, List, Optional, Type, Union

_homepage: str = metadata.metadata("gps_tracker")["Home-page"]


class GpsTrackerException(Exception):
    """Base class for gps-tracker exceptions."""


class UnknownDeviceType(GpsTrackerException):
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


class UnknownAnswerScheme(GpsTrackerException):
    """Exception raised when API answer cannot be interpreted."""

    def __init__(self, json_data, message, cls):
        """Store json and error message"""
        self.json_data = json_data
        self.message = message
        super().__init__(
            f"""
It appears that one of your devices has fields which are not currently recognized.
Please open an issue at {_homepage} with the following content:
{json.dumps(json_data, indent=4)}
{message} when instantiating {cls}.
Obfuscate any sensitive data by replacing letters by 'a' and digits by '0' if needed."""
        )


class ApiConnectionError(GpsTrackerException):
    """Exception raised if connection error occurs during API call."""


class HttpException(GpsTrackerException):
    """Base class for HTTP exceptions."""

    _registry: Dict[int, Type[HttpException]] = {}
    _default: Optional[Type[HttpException]] = None

    def __init_subclass__(cls, code: Optional[int] = None, default: bool = False):
        """Register subclass with its associated HTTP code."""
        if code is not None:
            if code not in HttpException._registry:
                HttpException._registry[code] = cls
            else:
                raise Exception(
                    f"Two subclasses defined " f"for HttpException with {code=}."
                )
        if default:
            HttpException._default = cls

    @staticmethod
    def get(code: int) -> Optional[Type[HttpException]]:
        """
        Return the subclass associated to code if it exists.

        :param code: HTTP code returned by the API call
        :type code: int
        :return: SubClass of HttpException with correct code if it exists
        :rtype: Type[HttpException]
        """
        if code in HttpException._registry:
            return HttpException._registry[code]
        return None

    @staticmethod
    def get_default() -> Optional[Type[HttpException]]:
        """Return the subclass declared as default."""
        return HttpException._default

    def _message(self) -> Optional[str]:  # pylint: disable=no-self-use
        """Define a specific message for the subclass"""
        return None

    def __init__(
        self, msg: Optional[str] = None, json_answer: Union[Dict, List, None] = None
    ):
        """Store json_answer if provided."""
        self.json_answer: Union[Dict, List, None] = json_answer

        if msg is None:
            msg = self._message()  # pylint: disable=assignment-from-none
        super().__init__(msg)


class UnauthorizedQuery(HttpException, code=401):
    """Exception raised if credentials are incorrect."""

    def _message(self) -> Optional[str]:
        """Return the "detail" message if provided by the API."""

        if (
            isinstance(self.json_answer, dict)
            and "detail" in self.json_answer
            and isinstance(self.json_answer["detail"], str)
        ):
            return self.json_answer["detail"]
        return None


class ForbiddenQuery(HttpException, code=403):
    """Exception raised when an API query is forbidden with current credentials."""

    def _message(self) -> Optional[str]:
        """Define message for forbidden queries."""
        return "You are not allowed to perform the attempted query."


class NoContentQuery(HttpException, code=204):
    """Exception raised when API has no content to return."""

    def _message(self) -> Optional[str]:
        """Define message for no-content queries."""
        return "No content is associated to this query."


class FailedQuery(HttpException, default=True):
    """Exception raised for any erroneous status code."""

    def _message(self) -> Optional[str]:
        """Define message for default exception."""
        return "Query failed with unexpected exception."
