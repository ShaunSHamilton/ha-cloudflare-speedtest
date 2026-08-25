"""Scheduled testing pause switch."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up pause switch."""
    async_add_entities((PauseScheduleSwitch(entry.runtime_data),))


class PauseScheduleSwitch(SpeedTestEntity, SwitchEntity):
    """Pause automatic speed tests."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SpeedTestCoordinator) -> None:
        super().__init__(coordinator, "pause")

    @property
    def is_on(self) -> bool:
        return self.coordinator.paused

    async def async_turn_on(self, **_kwargs: Any) -> None:
        await self.coordinator.async_set_paused(True)

    async def async_turn_off(self, **_kwargs: Any) -> None:
        await self.coordinator.async_set_paused(False)
