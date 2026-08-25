"""Cloudflare Speed Test integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import SpeedTestCoordinator

PLATFORM_TYPES = [Platform(platform) for platform in PLATFORMS]
type SpeedTestConfigEntry = ConfigEntry[SpeedTestCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: SpeedTestConfigEntry) -> bool:
    """Set up Cloudflare Speed Test from config entry."""
    coordinator = SpeedTestCoordinator(hass, entry)
    await coordinator.async_initialize()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORM_TYPES)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SpeedTestConfigEntry) -> bool:
    """Unload config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORM_TYPES)


async def _async_reload_entry(hass: HomeAssistant, entry: SpeedTestConfigEntry) -> None:
    """Reload after options change."""
    await hass.config_entries.async_reload(entry.entry_id)
