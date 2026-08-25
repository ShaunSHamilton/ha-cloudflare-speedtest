"""Speed-test state binary sensors."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import SpeedTestConfigEntry
from .coordinator import SpeedTestCoordinator
from .entity import SpeedTestEntity


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: SpeedTestConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors."""
    async_add_entities((SpeedTestProblem(entry.runtime_data), SpeedTestRunning(entry.runtime_data)))


class SpeedTestProblem(SpeedTestEntity, BinarySensorEntity):
    """Indicate latest test failure."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: SpeedTestCoordinator) -> None:
        super().__init__(coordinator, "problem")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data and self.coordinator.data.error)

    @property
    def extra_state_attributes(self) -> dict[str, str | None]:
        return {"error": self.coordinator.data.error if self.coordinator.data else None}


class SpeedTestRunning(SpeedTestEntity, BinarySensorEntity):
    """Indicate active test."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: SpeedTestCoordinator) -> None:
        super().__init__(coordinator, "testing")

    @property
    def is_on(self) -> bool:
        return self.coordinator.testing
