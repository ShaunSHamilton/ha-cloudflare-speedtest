"""Tests for aggregate traffic calculations."""

from custom_components.cloudflare_speedtest.coordinator import project_monthly_bytes


def test_project_monthly_bytes_uses_observed_average() -> None:
    """Projection scales average test cost by configured cadence."""
    assert project_monthly_bytes(18_000_000, 2, 60) == 6_480_000_000


def test_project_monthly_bytes_requires_completed_test() -> None:
    """Projection remains unknown before first successful test."""
    assert project_monthly_bytes(0, 0, 60) is None
