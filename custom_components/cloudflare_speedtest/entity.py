"""Shared Cloudflare Speed Test entity."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import SpeedTestCoordinator


class SpeedTestEntity(CoordinatorEntity[SpeedTestCoordinator]):
    """Base entity linked to speed-test coordinator."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SpeedTestCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_translation_key = key
