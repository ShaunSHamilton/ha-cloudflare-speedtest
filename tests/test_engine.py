"""Tests for speed-test result contracts."""

from datetime import UTC, datetime

from custom_components.cloudflare_speedtest.engine import SpeedTestResult, _stream_allocations


def test_total_bytes_combines_directions() -> None:
    """Traffic total includes upload and download payloads."""
    result = SpeedTestResult(datetime.now(UTC), 10, 5, 20, 2, 6_000_000, 3_000_000, "LHR")
    assert result.total_bytes == 9_000_000


def test_stream_allocations_preserve_byte_ceiling() -> None:
    """Parallel stream shares sum exactly to configured ceiling."""
    allocations = _stream_allocations(10, 4)
    assert allocations == (3, 3, 2, 2)
    assert sum(allocations) == 10
