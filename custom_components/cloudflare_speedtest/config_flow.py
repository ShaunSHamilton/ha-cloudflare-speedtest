"""Config flow for Cloudflare Speed Test."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig, NumberSelectorMode

from .const import CONF_INTERVAL, DEFAULT_INTERVAL, DOMAIN, MAX_INTERVAL, MIN_INTERVAL


def _interval_schema(value: int) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_INTERVAL, default=value): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_INTERVAL,
                    max=MAX_INTERVAL,
                    step=5,
                    mode=NumberSelectorMode.BOX,
                )
            )
        }
    )


class CloudflareSpeedTestConfigFlow(ConfigFlow, domain=DOMAIN):
    """Configure Cloudflare Speed Test."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Create single service entry."""
        if user_input is not None:
            return self.async_create_entry(
                title="Cloudflare Speed Test",
                data={CONF_INTERVAL: int(user_input[CONF_INTERVAL])},
            )
        return self.async_show_form(step_id="user", data_schema=_interval_schema(DEFAULT_INTERVAL))

    @staticmethod
    def async_get_options_flow(_config_entry: Any) -> CloudflareSpeedTestOptionsFlow:
        """Return options flow."""
        return CloudflareSpeedTestOptionsFlow()


class CloudflareSpeedTestOptionsFlow(OptionsFlow):
    """Change scheduling options."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(
                data={**self.config_entry.options, CONF_INTERVAL: int(user_input[CONF_INTERVAL])}
            )
        current = int(
            self.config_entry.options.get(CONF_INTERVAL, self.config_entry.data[CONF_INTERVAL])
        )
        return self.async_show_form(step_id="init", data_schema=_interval_schema(current))
