"""Config flow for the Smart-Me Local integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiohttp import BasicAuth, ClientError, ClientResponseError

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import APIAuthError, APIConnectionError, SmartMeLocalAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class SmartMeLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart-Me Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step shown in the UI."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]

            api = SmartMeLocalAPI(self.hass, host=host, username=username, password=password)

            try:
                data = await api.async_get_device_data()
            except APIAuthError:
                errors["base"] = "invalid_auth"
            except APIConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during Smart-Me Local setup")
                errors["base"] = "unknown"
            else:
                device_id = data.get("Id", host)
                device_name = data.get("Name", host)

                await self.async_set_unique_id(str(device_id))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=device_name,
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
