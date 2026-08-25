"""Config and options flows for Cloudflare Speed Test."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.data_entry_flow import section
from homeassistant.helpers.selector import NumberSelector, NumberSelectorConfig, NumberSelectorMode

from .const import (
    CONF_DOWNLOAD_BYTES,
    CONF_DOWNLOAD_SECONDS,
    CONF_INTERVAL,
    CONF_LATENCY_SAMPLES,
    CONF_MAX_TEST_SECONDS,
    CONF_READ_CHUNK_BYTES,
    CONF_STREAMS,
    CONF_UPLOAD_BYTES,
    CONF_UPLOAD_SECONDS,
    CONF_WRITE_CHUNK_BYTES,
    DOMAIN,
    OPTION_SPECS,
    default_options,
)

SECTIONS = {
    "schedule": (CONF_INTERVAL,),
    "measurement": (
        CONF_DOWNLOAD_SECONDS,
        CONF_UPLOAD_SECONDS,
        CONF_DOWNLOAD_BYTES,
        CONF_UPLOAD_BYTES,
        CONF_STREAMS,
        CONF_MAX_TEST_SECONDS,
        CONF_LATENCY_SAMPLES,
    ),
    "advanced": (CONF_READ_CHUNK_BYTES, CONF_WRITE_CHUNK_BYTES),
}


def _selector(key: str) -> NumberSelector:
    default, minimum, maximum, step = OPTION_SPECS[key]
    return NumberSelector(
        NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=NumberSelectorMode.BOX,
        )
    )


def _initial_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_INTERVAL, default=OPTION_SPECS[CONF_INTERVAL][0]): _selector(
                CONF_INTERVAL
            )
        }
    )


def _options_schema(current: dict[str, int | float]) -> vol.Schema:
    schema: dict[Any, Any] = {}
    for section_name, keys in SECTIONS.items():
        fields = {
            vol.Required(key, description={"suggested_value": current[key]}): _selector(key)
            for key in keys
        }
        schema[vol.Required(section_name)] = section(
            vol.Schema(fields), {"collapsed": section_name == "advanced"}
        )
    return vol.Schema(schema)


def _flatten_sections(user_input: dict[str, Any]) -> dict[str, int | float]:
    values: dict[str, int | float] = {}
    for section_name, keys in SECTIONS.items():
        submitted = user_input[section_name]
        for key in keys:
            default = OPTION_SPECS[key][0]
            value = submitted[key]
            values[key] = float(value) if isinstance(default, float) else int(value)
    return values


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
        return self.async_show_form(step_id="user", data_schema=_initial_schema())

    @staticmethod
    def async_get_options_flow(_config_entry: ConfigEntry) -> CloudflareSpeedTestOptionsFlow:
        """Return options flow."""
        return CloudflareSpeedTestOptionsFlow()


class CloudflareSpeedTestOptionsFlow(OptionsFlow):
    """Change schedule and measurement settings."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Manage integration options."""
        if user_input is not None:
            return self.async_create_entry(
                data={**self.config_entry.options, **_flatten_sections(user_input)}
            )
        current = {
            **default_options(),
            **self.config_entry.data,
            **self.config_entry.options,
        }
        return self.async_show_form(step_id="init", data_schema=_options_schema(current))
