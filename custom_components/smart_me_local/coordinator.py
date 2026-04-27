"""DataUpdateCoordinator for the Smart-Me Local integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import APIAuthError, APIConnectionError, SmartMeLocalAPI
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class SmartMeData:
    """Snapshot of a single poll cycle."""

    device_data: dict


class SmartMeCoordinator(DataUpdateCoordinator[SmartMeData]):
    """Coordinator that fetches data from the Smart-Me device every scan interval."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialise the coordinator."""
        self.device_id: str = ""
        self.device_name: str = config_entry.title

        self.api = SmartMeLocalAPI(
            hass,
            host=config_entry.data[CONF_HOST],
            username=config_entry.data[CONF_USERNAME],
            password=config_entry.data[CONF_PASSWORD],
        )

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_method=self._async_update_data,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> SmartMeData:
        """Fetch data from the local device API."""
        try:
            data = await self.api.async_get_device_data()
        except APIAuthError as exc:
            _LOGGER.error("Authentication failed for Smart-Me device: %s", exc)
            raise UpdateFailed(exc) from exc
        except APIConnectionError as exc:
            raise UpdateFailed(
                f"Error communicating with Smart-Me device: {exc}"
            ) from exc

        # Cache the device ID for entity unique IDs
        self.device_id = data.get("Id", config_entry_unique_id(self))
        self.device_name = data.get("Name", self.device_name)
        return SmartMeData(device_data=data)


def config_entry_unique_id(coordinator: SmartMeCoordinator) -> str:
    """Return a fallback unique ID derived from the API host."""
    return coordinator.api.base_url
