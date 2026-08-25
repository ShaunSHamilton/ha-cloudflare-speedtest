"""Constants and configurable limits for Cloudflare Speed Test."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "cloudflare_speedtest"
TEST_HOST: Final = "https://speed.cloudflare.com"
PLATFORMS: Final = ("binary_sensor", "button", "sensor", "switch")

CONF_INTERVAL: Final = "interval_minutes"
CONF_DOWNLOAD_SECONDS: Final = "download_seconds"
CONF_UPLOAD_SECONDS: Final = "upload_seconds"
CONF_DOWNLOAD_BYTES: Final = "max_download_bytes"
CONF_UPLOAD_BYTES: Final = "max_upload_bytes"
CONF_STREAMS: Final = "streams"
CONF_MAX_TEST_SECONDS: Final = "max_test_seconds"
CONF_LATENCY_SAMPLES: Final = "latency_samples"
CONF_READ_CHUNK_BYTES: Final = "read_chunk_bytes"
CONF_WRITE_CHUNK_BYTES: Final = "write_chunk_bytes"

# key: default, minimum, maximum, selector step
OPTION_SPECS: Final[dict[str, tuple[int | float, int | float, int | float, int | float]]] = {
    CONF_INTERVAL: (60, 5, 1440, 5),
    CONF_DOWNLOAD_SECONDS: (3.0, 0.5, 30.0, 0.5),
    CONF_UPLOAD_SECONDS: (3.0, 0.5, 30.0, 0.5),
    CONF_DOWNLOAD_BYTES: (6_000_000, 50_000, 10_000_000_000, 50_000),
    CONF_UPLOAD_BYTES: (3_000_000, 50_000, 10_000_000_000, 50_000),
    CONF_STREAMS: (4, 1, 16, 1),
    CONF_MAX_TEST_SECONDS: (20, 1, 120, 1),
    CONF_LATENCY_SAMPLES: (5, 2, 50, 1),
    CONF_READ_CHUNK_BYTES: (65_536, 1_024, 1_048_576, 1_024),
    CONF_WRITE_CHUNK_BYTES: (65_536, 1_024, 1_048_576, 1_024),
}

REQUEST_BYTES_MAX: Final = 25_000_000


def default_options() -> dict[str, int | float]:
    """Return fresh option defaults."""
    return {key: spec[0] for key, spec in OPTION_SPECS.items()}
