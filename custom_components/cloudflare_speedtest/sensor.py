"""Speed-test measurement sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfDataRate, UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SpeedTestConfigEntry
from .coordinator import SpeedTestCoordinator
from .entity import SpeedTestEntity


@dataclass(frozen=True, kw_only=True)
class SpeedSensorDescription(SensorEntityDescription):
    """Describe coordinator-backed measurement."""

    value_fn: Callable[[SpeedTestCoordinator], Any]
    attributes_fn: Callable[[SpeedTestCoordinator], dict[str, Any]] | None = None


def _status(coordinator: SpeedTestCoordinator) -> str:
    if coordinator.testing:
        return "testing"
    if coordinator.data is None:
        return "unknown"
    return "failed" if coordinator.data.error else "ok"


SENSORS = (
    SpeedSensorDescription(
        key="download",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda c: c.data.download_mbps if c.data and not c.data.error else None,
    ),
    SpeedSensorDescription(
        key="upload",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.MEGABITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda c: c.data.upload_mbps if c.data and not c.data.error else None,
    ),
    SpeedSensorDescription(
        key="latency",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda c: c.data.latency_ms if c.data and not c.data.error else None,
    ),
    SpeedSensorDescription(
        key="jitter",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda c: c.data.jitter_ms if c.data and not c.data.error else None,
    ),
    SpeedSensorDescription(
        key="test_data",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda c: c.data.total_bytes if c.data and not c.data.error else None,
        attributes_fn=lambda c: (
            {"download_bytes": c.data.download_bytes, "upload_bytes": c.data.upload_bytes}
            if c.data
            else {}
        ),
    ),
    SpeedSensorDescription(
        key="total_data",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda c: c.total_bytes,
        attributes_fn=lambda c: {"tests_completed": c.test_count},
    ),
    SpeedSensorDescription(
        key="projected_monthly_data",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.BYTES,
        suggested_unit_of_measurement=UnitOfInformation.GIGABYTES,
        value_fn=lambda c: c.projected_monthly_bytes,
    ),
    SpeedSensorDescription(
        key="last_test", device_class=SensorDeviceClass.TIMESTAMP, value_fn=lambda c: c.last_run
    ),
    SpeedSensorDescription(
        key="next_test",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda c: c.next_run,
    ),
    SpeedSensorDescription(
        key="status",
        device_class=SensorDeviceClass.ENUM,
        options=("ok", "testing", "failed", "unknown"),
        value_fn=_status,
        attributes_fn=lambda c: {
            "error": c.data.error if c.data else None,
            "server": c.data.server if c.data else "",
            "engine": "cloudflare",
        },
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: SpeedTestConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors."""
    async_add_entities(SpeedTestSensor(entry.runtime_data, description) for description in SENSORS)


class SpeedTestSensor(SpeedTestEntity, SensorEntity):
    """Coordinator-backed sensor."""

    entity_description: SpeedSensorDescription

    def __init__(
        self, coordinator: SpeedTestCoordinator, description: SpeedSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | int | str | datetime | None:
        """Return current sensor value."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return supporting measurement details."""
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator)
