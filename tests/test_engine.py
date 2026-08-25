"""Tests for speed-test result contracts."""

from datetime import UTC, datetime

from custom_components.cloudflare_speedtest.engine import SpeedTestResult


def test_total_bytes_combines_directions() -> None:
    """Traffic total includes upload and download payloads."""
    result = SpeedTestResult(datetime.now(UTC), 10, 5, 20, 2, 6_000_000, 3_000_000, "LHR")
    assert result.total_bytes == 9_000_000
