"""Tests for the Smart-Me Local API client (api.py)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import ClientResponseError, ClientError

from custom_components.smart_me_local.api import (
    APIAuthError,
    APIConnectionError,
    SmartMeLocalAPI,
)

from tests.conftest import DEVICE_DATA


class FakeHass:
    """Minimal hass stub."""


def _make_api(host: str = "192.168.1.100") -> SmartMeLocalAPI:
    hass = FakeHass()
    with patch(
        "custom_components.smart_me_local.api.async_get_clientsession",
        return_value=MagicMock(),
    ):
        return SmartMeLocalAPI(hass, host=host, username="SN123", password="0000")


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestSmartMeLocalAPISuccess:
    def test_base_url(self):
        api = _make_api("10.0.0.5")
        assert api.base_url == "http://10.0.0.5/api/device"

    @pytest.mark.asyncio
    async def test_get_device_data_returns_json(self):
        api = _make_api()

        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value=DEVICE_DATA)

        # Context-manager used by `async with session.get(...) as response`
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        api._session.get = MagicMock(return_value=mock_cm)

        result = await api.async_get_device_data()

        assert result == DEVICE_DATA
        assert api.connected is True

    @pytest.mark.asyncio
    async def test_connected_flag_false_before_first_call(self):
        api = _make_api()
        assert api.connected is False


# ---------------------------------------------------------------------------
# Auth errors
# ---------------------------------------------------------------------------

class TestSmartMeLocalAPIAuthError:
    @pytest.mark.asyncio
    async def test_raises_api_auth_error_on_401(self):
        api = _make_api()

        exc = ClientResponseError(request_info=MagicMock(), history=(), status=401)
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(side_effect=exc)

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        api._session.get = MagicMock(return_value=mock_cm)

        with pytest.raises(APIAuthError):
            await api.async_get_device_data()

        assert api.connected is False

    @pytest.mark.asyncio
    async def test_raises_api_auth_error_on_403(self):
        api = _make_api()

        exc = ClientResponseError(request_info=MagicMock(), history=(), status=403)
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(side_effect=exc)

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        api._session.get = MagicMock(return_value=mock_cm)

        with pytest.raises(APIAuthError):
            await api.async_get_device_data()


# ---------------------------------------------------------------------------
# Connection errors
# ---------------------------------------------------------------------------

class TestSmartMeLocalAPIConnectionError:
    @pytest.mark.asyncio
    async def test_raises_api_connection_error_on_client_error(self):
        api = _make_api()

        exc = ClientResponseError(request_info=MagicMock(), history=(), status=500)
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock(side_effect=exc)

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        api._session.get = MagicMock(return_value=mock_cm)

        with pytest.raises(APIConnectionError):
            await api.async_get_device_data()

    @pytest.mark.asyncio
    async def test_raises_api_connection_error_on_network_failure(self):
        api = _make_api()

        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(side_effect=ClientError("timeout"))
        mock_cm.__aexit__ = AsyncMock(return_value=False)
        api._session.get = MagicMock(return_value=mock_cm)

        with pytest.raises(APIConnectionError):
            await api.async_get_device_data()
