"""Tests for speed-test option handling."""

from custom_components.cloudflare_speedtest.config_flow import SECTIONS, _flatten_sections
from custom_components.cloudflare_speedtest.const import OPTION_SPECS


def test_flatten_sections_preserves_option_types() -> None:
    """Sectioned form values become flat typed coordinator options."""
    submitted = {
        section_name: {key: OPTION_SPECS[key][0] for key in keys}
        for section_name, keys in SECTIONS.items()
    }
    submitted["measurement"]["download_seconds"] = 2

    flattened = _flatten_sections(submitted)

    assert flattened["download_seconds"] == 2.0
    assert isinstance(flattened["download_seconds"], float)
    assert isinstance(flattened["streams"], int)
    assert set(flattened) == set(OPTION_SPECS)
