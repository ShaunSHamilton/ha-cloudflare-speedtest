"""Manual speed-test button."""

from homeassistant.components.button import ButtonEntity
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
    """Set up button."""
    async_add_entities((RunSpeedTestButton(entry.runtime_data),))


class RunSpeedTestButton(SpeedTestEntity, ButtonEntity):
    """Run speed test on demand."""

    def __init__(self, coordinator: SpeedTestCoordinator) -> None:
        super().__init__(coordinator, "run_test")

    async def async_press(self) -> None:
        """Run test regardless of paused schedule."""
        paused = self.coordinator.paused
        self.coordinator.paused = False
        try:
            await self.coordinator.async_request_refresh()
        finally:
            self.coordinator.paused = paused
            self.coordinator.async_update_listeners()
