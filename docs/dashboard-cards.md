# Dashboard cards

Integration ships four dashboard cards in `cloudflare-speedtest-card.js`. Cards use Home Assistant built-in cards only: no Mushroom, ApexCharts, or other frontend dependency. Home Assistant loads module automatically while integration is installed.

Add cards through dashboard **Add card** picker or paste YAML below. Default entity IDs suit new installations. Override entity options when Home Assistant assigned different IDs.

## Connection overview

Current rates, latency, schedule controls, and test state. Set gauge maximums for connection plan.

```yaml
type: custom:cloudflare-speedtest-overview-card
download_max: 1000
upload_max: 100
latency_max: 200
jitter_max: 100
```

## Seven-day performance

Hourly Home Assistant long-term statistics for throughput, latency, and jitter.

```yaml
type: custom:cloudflare-speedtest-performance-card
days_to_show: 7
period: hour
stat_type: mean
```

## Monitoring data cost

Current totals plus daily monitoring traffic from total-increasing statistics.

```yaml
type: custom:cloudflare-speedtest-data-card
days_to_show: 30
```

## Compact status and control

Latest measurements and one-tap manual test control.

```yaml
type: custom:cloudflare-speedtest-compact-card
```

## Entity overrides

Each card accepts relevant `<key>_entity` options. Available keys:

- `status_entity`
- `last_test_entity`
- `next_test_entity`
- `testing_entity`
- `problem_entity`
- `download_entity`
- `upload_entity`
- `latency_entity`
- `jitter_entity`
- `run_test_entity`
- `pause_entity`
- `last_test_data_entity`
- `total_data_entity`
- `projected_data_entity`

Example:

```yaml
type: custom:cloudflare-speedtest-compact-card
download_entity: sensor.wan_download
upload_entity: sensor.wan_upload
latency_entity: sensor.wan_latency
run_test_entity: button.wan_run_test
```

After integration upgrades, hard-refresh browser or reload Home Assistant frontend if old card code remains cached.
