"""Regression tests for namespaced entity IDs."""

from unittest.mock import AsyncMock, patch

import pytest
from custom_components.cloudflare_speedtest.const import CONF_INTERVAL, DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

LEGACY_ENTITIES = {
    "binary_sensor": {"problem": "problem", "testing": "testing"},
    "button": {"run_test": "run_test_now"},
    "sensor": {
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
    },
    "switch": {"pause": "pause_schedule"},
}


@pytest.mark.asyncio
async def test_setup_migrates_unnamespaced_entity_ids(
    hass: HomeAssistant, enable_custom_integrations: None
) -> None:
    """Existing generic IDs gain integration prefix during setup."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_INTERVAL: 60})
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    for platform, entities in LEGACY_ENTITIES.items():
        for unique_key, object_id in entities.items():
            registry.async_get_or_create(
                platform,
                DOMAIN,
                f"{entry.entry_id}_{unique_key}",
                suggested_object_id=object_id,
                config_entry=entry,
            )

    with patch(
        "custom_components.cloudflare_speedtest.coordinator.SpeedTestCoordinator.async_initialize",
        new=AsyncMock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    for platform, entities in LEGACY_ENTITIES.items():
        for object_id in entities.values():
            assert registry.async_get(f"{platform}.{object_id}") is None
            assert registry.async_get(f"{platform}.cloudflare_speed_test_{object_id}") is not None
