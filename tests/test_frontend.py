"""Tests for dashboard card registration."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from custom_components.cloudflare_speedtest import _CARD_PATH, _CARD_VERSION, async_setup


@pytest.mark.asyncio
async def test_async_setup_registers_dashboard_cards() -> None:
    """Integration serves and loads its bundled card module."""
    hass = Mock()
    hass.http.async_register_static_paths = AsyncMock()

    with patch("custom_components.cloudflare_speedtest.add_extra_js_url") as add_js:
        assert await async_setup(hass, {})

    configs = hass.http.async_register_static_paths.await_args.args[0]
    assert len(configs) == 1
    assert configs[0].url_path == _CARD_PATH
    assert configs[0].path.endswith("frontend/cloudflare-speedtest-card.js")
    assert configs[0].cache_headers is True
    add_js.assert_called_once_with(hass, f"{_CARD_PATH}?v={_CARD_VERSION}")
