"""Constants for Cloudflare Speed Test."""

from datetime import timedelta

DOMAIN = "cloudflare_speedtest"
CONF_INTERVAL = "interval_minutes"
DEFAULT_INTERVAL = 60
MIN_INTERVAL = 5
MAX_INTERVAL = 1440
PLATFORMS = ("binary_sensor", "button", "sensor", "switch")
TEST_HOST = "https://speed.cloudflare.com"
DOWNLOAD_BYTES = 6_000_000
UPLOAD_BYTES = 3_000_000
STREAMS = 4
UPDATE_INTERVAL = timedelta(minutes=DEFAULT_INTERVAL)
