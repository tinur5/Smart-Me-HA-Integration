"""Sensor platform for the Smart-Me Local integration.

Each physical quantity reported by the local API is exposed as a separate
Home Assistant sensor entity.  Entities that are rarely needed are
disabled by default so users can enable only what they want.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartMeCoordinator

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Sensor descriptions
# ---------------------------------------------------------------------------

@dataclass(frozen=True, kw_only=True)
class SmartMeSensorEntityDescription(SensorEntityDescription):
    """Augmented entity description for Smart-Me sensors."""

    value_fn: Callable[[dict], float | None]


def _kw_to_w(key: str) -> Callable[[dict], float | None]:
    """Return a callable that converts a kW field to Watts."""

    def _fn(data: dict) -> float | None:
        raw = data.get(key)
        if raw is None:
            return None
        return round(float(raw) * 1000, 1)

    return _fn


def _field(key: str, decimals: int = 2) -> Callable[[dict], float | None]:
    """Return a callable that reads a field and rounds it."""

    def _fn(data: dict) -> float | None:
        raw = data.get(key)
        if raw is None:
            return None
        return round(float(raw), decimals)

    return _fn


SENSOR_DESCRIPTIONS: tuple[SmartMeSensorEntityDescription, ...] = (
    # ---- Active Power -------------------------------------------------------
    SmartMeSensorEntityDescription(
        key="ActivePower",
        translation_key="active_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_kw_to_w("ActivePower"),
    ),
    SmartMeSensorEntityDescription(
        key="ActivePowerL1",
        translation_key="active_power_l1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_kw_to_w("ActivePowerL1"),
    ),
    SmartMeSensorEntityDescription(
        key="ActivePowerL2",
        translation_key="active_power_l2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_kw_to_w("ActivePowerL2"),
    ),
    SmartMeSensorEntityDescription(
        key="ActivePowerL3",
        translation_key="active_power_l3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_kw_to_w("ActivePowerL3"),
    ),
    # ---- Voltage ------------------------------------------------------------
    SmartMeSensorEntityDescription(
        key="Voltage",
        translation_key="voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_field("Voltage", 1),
    ),
    SmartMeSensorEntityDescription(
        key="VoltageL1",
        translation_key="voltage_l1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("VoltageL1", 1),
    ),
    SmartMeSensorEntityDescription(
        key="VoltageL2",
        translation_key="voltage_l2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("VoltageL2", 1),
    ),
    SmartMeSensorEntityDescription(
        key="VoltageL3",
        translation_key="voltage_l3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("VoltageL3", 1),
    ),
    # ---- Current ------------------------------------------------------------
    SmartMeSensorEntityDescription(
        key="Current",
        translation_key="current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_field("Current", 2),
    ),
    SmartMeSensorEntityDescription(
        key="CurrentL1",
        translation_key="current_l1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("CurrentL1", 2),
    ),
    SmartMeSensorEntityDescription(
        key="CurrentL2",
        translation_key="current_l2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("CurrentL2", 2),
    ),
    SmartMeSensorEntityDescription(
        key="CurrentL3",
        translation_key="current_l3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("CurrentL3", 2),
    ),
    # ---- Energy (counter readings) -----------------------------------------
    SmartMeSensorEntityDescription(
        key="CounterReading",
        translation_key="counter_reading",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=_field("CounterReading", 3),
    ),
    SmartMeSensorEntityDescription(
        key="CounterReadingImport",
        translation_key="counter_reading_import",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=_field("CounterReadingImport", 3),
    ),
    SmartMeSensorEntityDescription(
        key="CounterReadingExport",
        translation_key="counter_reading_export",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=False,
        value_fn=_field("CounterReadingExport", 3),
    ),
    # ---- Frequency ----------------------------------------------------------
    SmartMeSensorEntityDescription(
        key="Frequency",
        translation_key="frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("Frequency", 2),
    ),
    # ---- Power factor -------------------------------------------------------
    SmartMeSensorEntityDescription(
        key="PowerFactor",
        translation_key="power_factor",
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=_field("PowerFactor", 3),
    ),
)


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart-Me Local sensors from a config entry."""
    from . import RuntimeData  # local import to avoid circular dependency

    runtime_data: RuntimeData = hass.data[DOMAIN][config_entry.entry_id]
    coordinator: SmartMeCoordinator = runtime_data.coordinator

    device_info = DeviceInfo(
        identifiers={(DOMAIN, coordinator.device_id or config_entry.entry_id)},
        name=coordinator.device_name,
        manufacturer="smart-me AG",
    )

    async_add_entities(
        SmartMeSensor(coordinator, description, device_info)
        for description in SENSOR_DESCRIPTIONS
    )


# ---------------------------------------------------------------------------
# Entity class
# ---------------------------------------------------------------------------

class SmartMeSensor(CoordinatorEntity[SmartMeCoordinator], SensorEntity):
    """A single sensor entity backed by the Smart-Me coordinator."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    entity_description: SmartMeSensorEntityDescription

    def __init__(
        self,
        coordinator: SmartMeCoordinator,
        description: SmartMeSensorEntityDescription,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_device_info = device_info
        self._attr_unique_id = (
            f"{coordinator.device_id or coordinator.config_entry.entry_id}"
            f"-{description.key}"
        )

    @property
    def native_value(self) -> float | None:
        """Return the current sensor value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data.device_data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle fresh data from the coordinator."""
        self.async_write_ha_state()
