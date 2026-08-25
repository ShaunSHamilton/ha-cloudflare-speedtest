# Cloudflare Speed Test

Home Assistant custom integration measuring internet download speed, upload speed, latency, jitter, and test traffic against `speed.cloudflare.com`.

## Features

- Automatic tests every 5 minutes to 24 hours
- Configurable download/upload target durations and data ceilings
- Configurable parallel streams, latency samples, safety timeout, and transfer chunk sizes
- Manual **Run test now** button
- Pause switch
- Download, upload, latency, jitter, latest test traffic, cumulative traffic, projected monthly traffic, timestamps, status, problem, and running entities
- Persisted cumulative traffic across restarts

Default test transfers up to 6 MB down and 3 MB up. Each direction stops when its target duration or data ceiling is reached first. Results stay in Home Assistant.

## Dashboard cards

Ready-to-paste cards cover current connection health, seven-day trends, monitoring data cost, and compact test controls. See [dashboard card examples](docs/dashboard-cards.md). Built-in options require no frontend dependency; enhanced examples identify required HACS cards.

## Install with HACS

1. Open HACS.
2. Add `https://github.com/ShaunSHamilton/ha-cloudflare-speedtest` as custom repository with category **Integration**.
3. Install **Cloudflare Speed Test**.
4. Restart Home Assistant.
5. Add integration from **Settings > Devices & services**.

## Manual installation

Copy `custom_components/cloudflare_speedtest` into `<config>/custom_components/`, restart Home Assistant, then add integration from **Settings > Devices & services**.

## License

[MIT](LICENSE)
