"""Tests for the Smart-Me Local config flow (config_flow.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.smart_me_local.api import APIAuthError, APIConnectionError
from custom_components.smart_me_local.config_flow import SmartMeLocalConfigFlow
from custom_components.smart_me_local.const import DOMAIN

from tests.conftest import DEVICE_DATA


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_flow() -> SmartMeLocalConfigFlow:
    """Return a config-flow instance wired to a minimal hass stub."""
    flow = SmartMeLocalConfigFlow()
    flow.hass = MagicMock()
    flow.context = {}
    # Stub out unique-id helpers so they don't require a real HA core
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry", "title": "My Smart Meter", "data": {}})
    flow.async_show_form = MagicMock(return_value={"type": "form"})
    flow.async_abort = MagicMock(return_value={"type": "abort"})
    return flow


USER_INPUT = {
    "host": "192.168.1.100",
    "username": "SN123",
    "password": "0000",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestConfigFlowUser:
    @pytest.mark.asyncio
    async def test_shows_form_when_no_input(self):
        flow = _make_flow()
        result = await flow.async_step_user(user_input=None)
        flow.async_show_form.assert_called_once()
        assert result["type"] == "form"

    @pytest.mark.asyncio
    async def test_creates_entry_on_success(self):
        flow = _make_flow()

        with patch(
            "custom_components.smart_me_local.config_flow.SmartMeLocalAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.async_get_device_data = AsyncMock(return_value=DEVICE_DATA)
            mock_api_class.return_value = mock_api

            result = await flow.async_step_user(user_input=USER_INPUT)

        flow.async_create_entry.assert_called_once()
        assert result["type"] == "create_entry"

    @pytest.mark.asyncio
    async def test_shows_invalid_auth_error(self):
        flow = _make_flow()
        flow.async_show_form = MagicMock(return_value={"type": "form", "errors": {"base": "invalid_auth"}})

        with patch(
            "custom_components.smart_me_local.config_flow.SmartMeLocalAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.async_get_device_data = AsyncMock(side_effect=APIAuthError("bad creds"))
            mock_api_class.return_value = mock_api

            result = await flow.async_step_user(user_input=USER_INPUT)

        call_kwargs = flow.async_show_form.call_args
        errors = call_kwargs.kwargs.get("errors", call_kwargs[1].get("errors", {}))
        assert errors.get("base") == "invalid_auth"

    @pytest.mark.asyncio
    async def test_shows_cannot_connect_error(self):
        flow = _make_flow()

        with patch(
            "custom_components.smart_me_local.config_flow.SmartMeLocalAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.async_get_device_data = AsyncMock(
                side_effect=APIConnectionError("timeout")
            )
            mock_api_class.return_value = mock_api

            result = await flow.async_step_user(user_input=USER_INPUT)

        call_kwargs = flow.async_show_form.call_args
        errors = call_kwargs.kwargs.get("errors", call_kwargs[1].get("errors", {}))
        assert errors.get("base") == "cannot_connect"

    @pytest.mark.asyncio
    async def test_shows_unknown_error_on_unexpected_exception(self):
        flow = _make_flow()

        with patch(
            "custom_components.smart_me_local.config_flow.SmartMeLocalAPI"
        ) as mock_api_class:
            mock_api = MagicMock()
            mock_api.async_get_device_data = AsyncMock(
                side_effect=RuntimeError("something broke")
            )
            mock_api_class.return_value = mock_api

            result = await flow.async_step_user(user_input=USER_INPUT)

        call_kwargs = flow.async_show_form.call_args
        errors = call_kwargs.kwargs.get("errors", call_kwargs[1].get("errors", {}))
        assert errors.get("base") == "unknown"
