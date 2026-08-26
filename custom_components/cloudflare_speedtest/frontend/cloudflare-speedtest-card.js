const DEFAULT_ENTITIES = {
  status: "sensor.cloudflare_speed_test_status",
  last_test: "sensor.cloudflare_speed_test_last_test",
  next_test: "sensor.cloudflare_speed_test_next_test",
  testing: "binary_sensor.cloudflare_speed_test_testing",
  problem: "binary_sensor.cloudflare_speed_test_problem",
  download: "sensor.cloudflare_speed_test_download",
  upload: "sensor.cloudflare_speed_test_upload",
  latency: "sensor.cloudflare_speed_test_latency",
  jitter: "sensor.cloudflare_speed_test_jitter",
  run_test: "button.cloudflare_speed_test_run_test_now",
  pause: "switch.cloudflare_speed_test_pause_schedule",
  last_test_data: "sensor.cloudflare_speed_test_last_test_data",
  total_data: "sensor.cloudflare_speed_test_total_data_used",
  projected_data: "sensor.cloudflare_speed_test_projected_monthly_data",
};

const entity = (config, key) => config[`${key}_entity`] ?? DEFAULT_ENTITIES[key];

class CloudflareSpeedTestNativeCard extends HTMLElement {
  setConfig(config) {
    this.config = { ...config };
    this.card = undefined;
    this.loading = false;
    this.replaceChildren();
    this.buildCard();
  }

  set hass(hass) {
    this._hass = hass;
    if (this.card) this.card.hass = hass;
  }

  connectedCallback() {
    this.buildCard();
  }

  async buildCard() {
    if (!this.config || this.loading || this.card) return;
    this.loading = true;
    const helpers = await window.loadCardHelpers();
    if (!this.isConnected && !this.config) return;
    this.card = helpers.createCardElement(this.cardConfig(this.config));
    if (this._hass) this.card.hass = this._hass;
    this.replaceChildren(this.card);
    this.loading = false;
  }

  getCardSize() {
    return this.card?.getCardSize?.() ?? this.constructor.cardSize;
  }
}

class CloudflareSpeedTestOverviewCard extends CloudflareSpeedTestNativeCard {
  static cardSize = 10;

  cardConfig(config) {
    return {
      type: "vertical-stack",
      cards: [
        {
          type: "entities",
          title: config.title ?? "Internet connection",
          show_header_toggle: false,
          entities: [
            entity(config, "status"),
            entity(config, "last_test"),
            entity(config, "next_test"),
            entity(config, "testing"),
            entity(config, "problem"),
          ],
        },
        {
          type: "grid",
          columns: 2,
          square: false,
          cards: [
            gauge(config, "download", "Download", config.download_max ?? 1000, 50, 100),
            gauge(config, "upload", "Upload", config.upload_max ?? 100, 10, 25),
            gauge(config, "latency", "Latency", config.latency_max ?? 200, 50, 100, true),
            gauge(config, "jitter", "Jitter", config.jitter_max ?? 100, 20, 50, true),
          ],
        },
        {
          type: "entities",
          show_header_toggle: false,
          entities: [entity(config, "run_test"), entity(config, "pause")],
        },
      ],
    };
  }
}

function gauge(config, key, name, max, warning, critical, lowerIsBetter = false) {
  return {
    type: "gauge",
    entity: entity(config, key),
    name,
    min: 0,
    max,
    needle: true,
    severity: lowerIsBetter
      ? { green: 0, yellow: warning, red: critical }
      : { red: 0, yellow: warning, green: critical },
  };
}

class CloudflareSpeedTestPerformanceCard extends CloudflareSpeedTestNativeCard {
  static cardSize = 8;

  cardConfig(config) {
    const common = {
      type: "statistics-graph",
      chart_type: "line",
      period: config.period ?? "hour",
      days_to_show: config.days_to_show ?? 7,
      stat_types: [config.stat_type ?? "mean"],
      hide_legend: false,
    };
    return {
      type: "vertical-stack",
      cards: [
        {
          ...common,
          title: config.title ?? "Internet performance - 7 days",
          entities: [entity(config, "download"), entity(config, "upload")],
        },
        {
          ...common,
          title: config.latency_title ?? "Connection responsiveness",
          entities: [entity(config, "latency"), entity(config, "jitter")],
        },
      ],
    };
  }
}

class CloudflareSpeedTestDataCard extends CloudflareSpeedTestNativeCard {
  static cardSize = 6;

  cardConfig(config) {
    return {
      type: "vertical-stack",
      cards: [
        {
          type: "entities",
          title: config.title ?? "Speed-test data usage",
          show_header_toggle: false,
          entities: [
            entity(config, "last_test_data"),
            entity(config, "total_data"),
            entity(config, "projected_data"),
          ],
        },
        {
          type: "statistics-graph",
          title: config.graph_title ?? "Daily test traffic",
          chart_type: "bar",
          period: "day",
          days_to_show: config.days_to_show ?? 30,
          stat_types: ["change"],
          entities: [entity(config, "total_data")],
        },
      ],
    };
  }
}

class CloudflareSpeedTestCompactCard extends CloudflareSpeedTestNativeCard {
  static cardSize = 4;

  cardConfig(config) {
    return {
      type: "vertical-stack",
      cards: [
        {
          type: "glance",
          title: config.title ?? "Internet connection",
          show_name: true,
          show_state: true,
          columns: 4,
          entities: [
            entity(config, "download"),
            entity(config, "upload"),
            entity(config, "latency"),
            entity(config, "status"),
          ],
        },
        {
          type: "button",
          entity: entity(config, "run_test"),
          name: config.button_name ?? "Run speed test",
          show_state: false,
          tap_action: {
            action: "perform-action",
            perform_action: "button.press",
            target: { entity_id: entity(config, "run_test") },
          },
        },
      ],
    };
  }
}

const cards = [
  ["cloudflare-speedtest-overview-card", CloudflareSpeedTestOverviewCard, "Cloudflare Speed Test Overview", "Connection state, measurements, and controls."],
  ["cloudflare-speedtest-performance-card", CloudflareSpeedTestPerformanceCard, "Cloudflare Speed Test Performance", "Seven-day throughput and responsiveness charts."],
  ["cloudflare-speedtest-data-card", CloudflareSpeedTestDataCard, "Cloudflare Speed Test Data Usage", "Test traffic totals and daily usage."],
  ["cloudflare-speedtest-compact-card", CloudflareSpeedTestCompactCard, "Cloudflare Speed Test Compact", "Compact measurements and test control."],
];

window.customCards = window.customCards || [];
for (const [type, cardClass, name, description] of cards) {
  if (!customElements.get(type)) customElements.define(type, cardClass);
  if (!window.customCards.some((card) => card.type === type)) {
    window.customCards.push({ type, name, description, preview: true });
  }
}
