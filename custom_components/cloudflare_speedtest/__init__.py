"""Cloudflare Speed Test integration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, PLATFORMS
from .coordinator import SpeedTestCoordinator

PLATFORM_TYPES = [Platform(platform) for platform in PLATFORMS]
type SpeedTestConfigEntry = ConfigEntry[SpeedTestCoordinator]

# Entity IDs generated before service device metadata was added. Restrict migration
# to exact integration-owned IDs so user-customized IDs remain untouched.
_LEGACY_OBJECT_IDS = {
    "problem": "problem",
    "testing": "testing",
    "run_test": "run_test_now",
    "download": "download",
    "upload": "upload",
    "latency": "latency",
    "jitter": "jitter",
    "test_data": "last_test_data",
    "total_data": "total_data_used",
    "projected_monthly_data": "projected_monthly_data",
    "last_test": "last_test",
    "next_test": "next_test",
    "status": "status",
    "pause": "pause_schedule",
}
_ENTITY_ID_PREFIX = "cloudflare_speed_test_"
_CARD_PATH = "/cloudflare_speedtest/cloudflare-speedtest-card.js"
_CARD_VERSION = "0.5.0"


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Serve and register dependency-free dashboard cards."""
    card_file = Path(__file__).parent / "frontend" / "cloudflare-speedtest-card.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(_CARD_PATH, str(card_file), cache_headers=True)]
    )
    add_extra_js_url(hass, f"{_CARD_PATH}?v={_CARD_VERSION}")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: SpeedTestConfigEntry) -> bool:
    """Set up Cloudflare Speed Test from config entry."""
    _async_migrate_entity_ids(hass, entry)
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


def _async_migrate_entity_ids(hass: HomeAssistant, entry: SpeedTestConfigEntry) -> None:
    """Namespace generic entity IDs created by initial releases."""
    registry = er.async_get(hass)
    for unique_key, legacy_object_id in _LEGACY_OBJECT_IDS.items():
        unique_id = f"{entry.entry_id}_{unique_key}"
        for platform in PLATFORM_TYPES:
            entity_id = registry.async_get_entity_id(platform, DOMAIN, unique_id)
            if entity_id != f"{platform}.{legacy_object_id}":
                continue
            new_entity_id = registry.async_get_available_entity_id(
                platform,
                f"{_ENTITY_ID_PREFIX}{legacy_object_id}",
                current_entity_id=entity_id,
            )
            registry.async_update_entity(entity_id, new_entity_id=new_entity_id)
            break
