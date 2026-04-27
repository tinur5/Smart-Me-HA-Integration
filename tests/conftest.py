"""Shared test fixtures for smart_me_local tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

DEVICE_DATA = {
    "Id": "test-device-id-1234",
    "Name": "My Smart Meter",
    "Serial": "SN12345678",
    "DeviceType": 2,
    "ActivePower": 1.5,      # kW  → 1500 W
    "ActivePowerL1": 0.6,
    "ActivePowerL2": 0.5,
    "ActivePowerL3": 0.4,
    "Voltage": 230.1,
    "VoltageL1": 230.1,
    "VoltageL2": 229.8,
    "VoltageL3": 230.4,
    "Current": 6.52,
    "CurrentL1": 2.6,
    "CurrentL2": 2.17,
    "CurrentL3": 1.74,
    "CounterReading": 1234.567,
    "CounterReadingImport": 1234.567,
    "CounterReadingExport": 0.0,
    "Frequency": 50.02,
    "PowerFactor": 0.998,
}
