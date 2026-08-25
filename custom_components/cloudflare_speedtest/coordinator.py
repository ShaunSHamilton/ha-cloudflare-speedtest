"""Scheduling and persisted aggregate state."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_INTERVAL, DOMAIN, default_options
from .engine import CloudflareSpeedTest, SpeedTestResult

_STORE_VERSION = 1
_LOGGER = logging.getLogger(__name__)


def project_monthly_bytes(total_bytes: int, test_count: int, interval_minutes: int) -> int | None:
    """Project 30-day traffic from average observed test cost."""
    if not test_count:
        return None
    tests_per_month = 30 * 24 * 60 / interval_minutes
    return round(total_bytes / test_count * tests_per_month)


class SpeedTestCoordinator(DataUpdateCoordinator[SpeedTestResult | None]):
    """Run tests and expose current and aggregate results."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry[Any]) -> None:
        self.entry = entry
        self.options = {**default_options(), **entry.data, **entry.options}
        self.testing = False
        self.paused = bool(entry.options.get("paused", False))
        self.total_bytes = 0
        self.test_count = 0
        self.last_run: datetime | None = None
        self._store = Store[dict[str, Any]](hass, _STORE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        interval = int(self.options[CONF_INTERVAL])
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval),
        )
        self._engine = CloudflareSpeedTest(async_get_clientsession(hass))

    @property
    def interval_minutes(self) -> int:
        """Configured test interval."""
        return int(self.update_interval.total_seconds() // 60) if self.update_interval else 0

    @property
    def next_run(self) -> datetime | None:
        """Next expected scheduled run."""
        if self.paused or self.last_run is None:
            return None
        return self.last_run + self.update_interval

    @property
    def projected_monthly_bytes(self) -> int | None:
        """Project monthly traffic from observed average test cost."""
        return project_monthly_bytes(self.total_bytes, self.test_count, self.interval_minutes)

    async def async_initialize(self) -> None:
        """Restore aggregate state, then run first test."""
        stored = await self._store.async_load() or {}
        self.total_bytes = int(stored.get("total_bytes", 0))
        self.test_count = int(stored.get("test_count", 0))
        if last_run := stored.get("last_run"):
            self.last_run = datetime.fromisoformat(last_run)
        await self.async_config_entry_first_refresh()

    async def _async_update_data(self) -> SpeedTestResult | None:
        if self.paused:
            return self.data
        self.testing = True
        self.async_update_listeners()
        try:
            result = await self._engine.async_run(self.options)
        finally:
            self.testing = False
        self.last_run = result.timestamp
        if result.error is None:
            self.total_bytes += result.total_bytes
            self.test_count += 1
        await self._store.async_save(
            {
                "total_bytes": self.total_bytes,
                "test_count": self.test_count,
                "last_run": self.last_run.astimezone(UTC).isoformat(),
            }
        )
        return result

    async def async_set_paused(self, paused: bool) -> None:
        """Pause or resume scheduled tests without reloading integration."""
        self.paused = paused
        self.hass.config_entries.async_update_entry(
            self.entry, options={**self.entry.options, "paused": paused}
        )
        self.async_update_listeners()
