# Dashboard cards

Copy any card into Home Assistant dashboard YAML editor. Entity IDs below are defaults for new installations. Select corresponding entities from entity picker if Home Assistant assigned different IDs.

## Connection overview

Dependency-free summary with current rates, latency, schedule controls, and test state. Adjust gauge maximums for connection plan.

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Internet connection
    show_header_toggle: false
    entities:
      - entity: sensor.cloudflare_speed_test_status
      - entity: sensor.cloudflare_speed_test_last_test
      - entity: sensor.cloudflare_speed_test_next_test
      - entity: binary_sensor.cloudflare_speed_test_testing
      - entity: binary_sensor.cloudflare_speed_test_problem
  - type: grid
    columns: 2
    square: false
    cards:
      - type: gauge
        entity: sensor.cloudflare_speed_test_download
        name: Download
        min: 0
        max: 1000
        needle: true
        severity:
          red: 0
          yellow: 50
          green: 100
      - type: gauge
        entity: sensor.cloudflare_speed_test_upload
        name: Upload
        min: 0
        max: 100
        needle: true
        severity:
          red: 0
          yellow: 10
          green: 25
      - type: gauge
        entity: sensor.cloudflare_speed_test_latency
        name: Latency
        min: 0
        max: 200
        needle: true
        severity:
          green: 0
          yellow: 50
          red: 100
      - type: gauge
        entity: sensor.cloudflare_speed_test_jitter
        name: Jitter
        min: 0
        max: 100
        needle: true
        severity:
          green: 0
          yellow: 20
          red: 50
  - type: entities
    show_header_toggle: false
    entities:
      - entity: button.cloudflare_speed_test_run_test_now
      - entity: switch.cloudflare_speed_test_pause_schedule
```

## Seven-day performance

Requires [ApexCharts Card](https://github.com/RomRider/apexcharts-card). Hourly averages keep long histories readable. Separate axes prevent latency from flattening throughput lines.

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Internet performance - 7 days
  show_states: true
  colorize_states: true
graph_span: 7d
update_interval: 5min
yaxis:
  - id: speed
    min: 0
    decimals: 0
    apex_config:
      title:
        text: Mbps
  - id: latency
    min: 0
    opposite: true
    decimals: 0
    apex_config:
      title:
        text: ms
all_series_config:
  stroke_width: 2
  group_by:
    duration: 1h
    func: avg
series:
  - entity: sensor.cloudflare_speed_test_download
    name: Download
    yaxis_id: speed
    color: "#2196f3"
  - entity: sensor.cloudflare_speed_test_upload
    name: Upload
    yaxis_id: speed
    color: "#4caf50"
  - entity: sensor.cloudflare_speed_test_latency
    name: Latency
    yaxis_id: latency
    color: "#ff9800"
    stroke_width: 1
```

## Monitoring data cost

Dependency-free daily usage graph plus current totals. `total_data_used` uses total-increasing statistics, so daily change represents monitoring traffic spent each day.

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Speed-test data usage
    show_header_toggle: false
    entities:
      - entity: sensor.cloudflare_speed_test_last_test_data
      - entity: sensor.cloudflare_speed_test_total_data_used
      - entity: sensor.cloudflare_speed_test_projected_monthly_data
  - type: statistics-graph
    title: Daily test traffic
    chart_type: bar
    period: day
    days_to_show: 30
    stat_types:
      - change
    entities:
      - sensor.cloudflare_speed_test_total_data_used
```

## Compact status and control

Requires [Mushroom](https://github.com/piitaya/lovelace-mushroom). Card summarizes latest result; tapping icon starts test while tapping card opens status details.

```yaml
type: custom:mushroom-template-card
entity: sensor.cloudflare_speed_test_status
entity_id:
  - sensor.cloudflare_speed_test_download
  - sensor.cloudflare_speed_test_upload
  - sensor.cloudflare_speed_test_latency
  - binary_sensor.cloudflare_speed_test_testing
primary: >-
  {% if is_state('binary_sensor.cloudflare_speed_test_testing', 'on') %}
    Running speed test...
  {% else %}
    {{ states('sensor.cloudflare_speed_test_download') }} Mbps down
  {% endif %}
secondary: >-
  {{ states('sensor.cloudflare_speed_test_upload') }} Mbps up ·
  {{ states('sensor.cloudflare_speed_test_latency') }} ms latency
icon: >-
  {% if is_state('binary_sensor.cloudflare_speed_test_testing', 'on') %}
    mdi:speedometer-slow
  {% elif is_state(entity, 'failed') %}
    mdi:alert-circle
  {% else %}
    mdi:speedometer
  {% endif %}
color: >-
  {% if is_state('binary_sensor.cloudflare_speed_test_testing', 'on') %}
    blue
  {% elif is_state(entity, 'failed') %}
    red
  {% else %}
    green
  {% endif %}
tap_action:
  action: more-info
icon_tap_action:
  action: perform-action
  perform_action: button.press
  target:
    entity_id: button.cloudflare_speed_test_run_test_now
```
