"""URL provider for specific Invoxia API queries."""

from typing import Optional

from .datatypes import Device


class UrlProvider:
    """URL provider generates the API urls used to access user data."""

    def __init__(self, api_url: str = "https://labs.invoxia.io"):
        """
        Initialize provider with the API domain.

        :param api_url: URL of the Invoxia API, defaults to https://labs.invoxia.io
        :type api_url: str
        """
        self.api_url: str = api_url

    def _form_url(self, path: str) -> str:
        """
        Form the full url from the base api and the given path.

        :param path: path to associate to the API base URL
        :type path: str

        :return: complete url
        :rtype: str
        """
        return f"{self.api_url}/{path}"

    def users(self) -> str:
        """
        Form the URL to access list of users associated with credentials.

        :return: API URL
        :rtype: str
        """
        return self._form_url("users/")

    def user(self, user_id: int) -> str:
        """
        Form the URL to access a specific user by its id.

        :param user_id: user unique identifier
        :type user_id: int

        :return: API URL
        :rtype: str
        """
        return self._form_url(f"users/{user_id}/")

    def devices(self, kind: Optional[str] = None) -> str:
        """
        Form the URL to access all devices associated with current credentials.

        :param kind: Kind of device to list (tracker, android, iphone)
        :type kind: str, optional

        :return: API URL
        :rtype: str
        """
        arg = ""
        if kind is not None:
            if kind in Device.get_types():
                arg = f"?type={kind}"
            else:
                raise KeyError(f"Device of kind '{kind}' are undefined.")

        return self._form_url(f"devices/{arg}")

    def device(self, device_id: int) -> str:
        """
        Form the URL to access a specific device by its id.

        :param device_id: device unique identifier
        :type device_id: int

        :return: API URL
        :rtype: str
        """
        return self._form_url(f"devices/{device_id}/")

    def locations(
        self,
        device_id: int,
        not_before: Optional[int] = None,
        not_after: Optional[int] = None,
    ) -> str:
        """
        Form the URL to access tracker locations in a given time-range.

        :param device_id: tracker device unique identifier
        :type device_id: int

        :param not_before: timestamp of the minimum datetime to consider
        :type not_before: int, optional

        :param not_after: timestamp of the maximum datetime to consider
        :type not_after: int, optional

        :return: API URL
        :rtype: str
        """
        args = []
        if not_before is not None:
            args.append(f"timestamp={not_before}")
        if not_after is not None:
            args.append(f"timestamp_max={not_after}")
        args_str = f"?{'&'.join(args)}" if args else ""

        return self._form_url(f"devices/{device_id}/tracker_data/{args_str}")

    def tracker_status(self, device_id: int) -> str:
        """Form the URL to get the current tracker status."""
        return self._form_url(f"devices/{device_id}/tracker_status/")

    def tracker_config(self, device_id: int) -> str:
        """Form the URL to get the current tracker config."""
        return self._form_url(f"devices/{device_id}/tracker_config/")
