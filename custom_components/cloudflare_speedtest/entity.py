"""Shared Cloudflare Speed Test entity."""

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, TEST_HOST
from .coordinator import SpeedTestCoordinator


class SpeedTestEntity(CoordinatorEntity[SpeedTestCoordinator]):
    """Base entity linked to speed-test coordinator."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SpeedTestCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            entry_type=DeviceEntryType.SERVICE,
            manufacturer="Cloudflare",
            model="Internet speed test",
            name="Cloudflare Speed Test",
            configuration_url=TEST_HOST,
        )
