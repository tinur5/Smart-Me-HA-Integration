"""Tests for the Smart-Me Local sensor platform (sensor.py)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from custom_components.smart_me_local.sensor import (
    SENSOR_DESCRIPTIONS,
    SmartMeSensor,
    SmartMeSensorEntityDescription,
    _field,
    _kw_to_w,
)
from custom_components.smart_me_local.coordinator import SmartMeData

from tests.conftest import DEVICE_DATA


# ---------------------------------------------------------------------------
# Helper: value function factories
# ---------------------------------------------------------------------------

class TestValueFunctions:
    def test_kw_to_w_converts_correctly(self):
        fn = _kw_to_w("ActivePower")
        assert fn({"ActivePower": 1.5}) == 1500.0

    def test_kw_to_w_returns_none_for_missing_key(self):
        fn = _kw_to_w("ActivePower")
        assert fn({}) is None

    def test_field_rounds_correctly(self):
        fn = _field("Voltage", 1)
        assert fn({"Voltage": 230.123}) == 230.1

    def test_field_returns_none_for_missing_key(self):
        fn = _field("Voltage", 1)
        assert fn({}) is None


# ---------------------------------------------------------------------------
# Helper: sensor descriptions are well-formed
# ---------------------------------------------------------------------------

class TestSensorDescriptions:
    def test_all_descriptions_have_unique_keys(self):
        keys = [desc.key for desc in SENSOR_DESCRIPTIONS]
        assert len(keys) == len(set(keys))

    def test_active_power_description_unit(self):
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "ActivePower")
        assert desc.native_unit_of_measurement == "W"

    def test_counter_reading_description_unit(self):
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "CounterReading")
        assert desc.native_unit_of_measurement == "kWh"

    def test_voltage_description_unit(self):
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "Voltage")
        assert desc.native_unit_of_measurement == "V"


# ---------------------------------------------------------------------------
# Helper: SmartMeSensor native_value
# ---------------------------------------------------------------------------

def _make_sensor(key: str) -> SmartMeSensor:
    """Build a SmartMeSensor with a mocked coordinator holding DEVICE_DATA."""
    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == key)
    coordinator = MagicMock()
    coordinator.data = SmartMeData(device_data=DEVICE_DATA)
    coordinator.device_id = "test-device-id-1234"
    coordinator.config_entry = MagicMock()
    coordinator.config_entry.entry_id = "entry_123"

    device_info = MagicMock()
    sensor = SmartMeSensor.__new__(SmartMeSensor)
    sensor.coordinator = coordinator
    sensor.entity_description = desc
    sensor._attr_device_info = device_info
    sensor._attr_unique_id = f"{coordinator.device_id}-{key}"
    return sensor


class TestSmartMeSensorNativeValue:
    def test_active_power_value(self):
        sensor = _make_sensor("ActivePower")
        # DEVICE_DATA["ActivePower"] = 1.5 kW → 1500.0 W
        assert sensor.native_value == pytest.approx(1500.0)

    def test_voltage_value(self):
        sensor = _make_sensor("Voltage")
        assert sensor.native_value == pytest.approx(230.1)

    def test_current_value(self):
        sensor = _make_sensor("Current")
        assert sensor.native_value == pytest.approx(6.52)

    def test_counter_reading_value(self):
        sensor = _make_sensor("CounterReading")
        assert sensor.native_value == pytest.approx(1234.567)

    def test_frequency_value(self):
        sensor = _make_sensor("Frequency")
        assert sensor.native_value == pytest.approx(50.02)

    def test_power_factor_value(self):
        sensor = _make_sensor("PowerFactor")
        assert sensor.native_value == pytest.approx(0.998)

    def test_returns_none_when_coordinator_data_is_none(self):
        desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "ActivePower")
        coordinator = MagicMock()
        coordinator.data = None
        sensor = SmartMeSensor.__new__(SmartMeSensor)
        sensor.coordinator = coordinator
        sensor.entity_description = desc
        assert sensor.native_value is None

    def test_returns_none_when_field_missing_in_data(self):
        sensor = _make_sensor("ActivePowerL1")
        # Override coordinator data to have no ActivePowerL1
        sensor.coordinator.data = SmartMeData(device_data={})
        assert sensor.native_value is None
