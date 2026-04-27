"""Async API client for the Smart-Me local device API.

The Smart-Me meter exposes a REST API on the local network at
``http://<device-ip>/api/device``.  Authentication uses HTTP Basic Auth
where the username is the device serial number and the password is the
device password (factory default: ``0000``).
"""

from __future__ import annotations

import logging

from aiohttp import BasicAuth, ClientError, ClientResponseError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import API_PATH

_LOGGER = logging.getLogger(__name__)


class SmartMeLocalAPI:
    """Async client for the Smart-Me local REST API."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
    ) -> None:
        """Initialise the API client.

        Args:
            hass: The Home Assistant instance (used to obtain the shared
                  aiohttp client session).
            host: IP address or hostname of the Smart-Me device
                  (e.g. ``192.168.1.100``).
            username: Device serial number used as Basic-Auth username.
            password: Device password used as Basic-Auth password.
        """
        self._host = host
        self._auth = BasicAuth(username, password)
        self._session = async_get_clientsession(hass)
        self.connected: bool = False

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        """Return the base URL for the device API."""
        return f"http://{self._host}{API_PATH}"

    async def async_get_device_data(self) -> dict:
        """Fetch live data from the device.

        Returns:
            A dictionary with all fields returned by the local API
            (e.g. ``ActivePower``, ``CounterReading``, ``VoltageL1`` …).

        Raises:
            APIAuthError: When the device returns HTTP 401/403.
            APIConnectionError: When the device cannot be reached at all.
        """
        try:
            async with self._session.get(
                url=self.base_url,
                auth=self._auth,
            ) as response:
                response.raise_for_status()
                data: dict = await response.json()
                self.connected = True
                return data
        except ClientResponseError as exc:
            self.connected = False
            if exc.status in (401, 403):
                raise APIAuthError(
                    "Invalid credentials for Smart-Me device."
                ) from exc
            raise APIConnectionError(
                f"Unexpected HTTP {exc.status} from Smart-Me device."
            ) from exc
        except ClientError as exc:
            self.connected = False
            raise APIConnectionError(
                f"Cannot connect to Smart-Me device at {self._host}: {exc}"
            ) from exc


class APIAuthError(Exception):
    """Raised when the device rejects the supplied credentials."""


class APIConnectionError(Exception):
    """Raised when the device cannot be reached."""
