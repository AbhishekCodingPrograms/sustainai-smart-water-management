# Security privacy and optional sensor path

## Current boundary

The demo reads local CSVs in memory, trains locally and saves only ticket IDs, inspection notes/outcomes and UTC update times in SQLite. It does not transmit telemetry to an AI API. Streamlit serves data to connected browser users, so bind to localhost for a private demo. The app has no login or user separation; users of a shared instance can see the same inspection history. Avoid sensitive household patterns, addresses, names, precise locations or personal information. CSV exports may contain operational information; access and delete them appropriately.

Uploads are capped at 5 MB, 50,000 rows and explicit numeric ranges; columns outside the contract are discarded. SQL writes use parameters. Exported text neutralizes common spreadsheet formula prefixes. These controls are not a comprehensive penetration test. The SQLite database is not encrypted or tamper evident. Notes are shown as text, not rendered as unsafe HTML. Never commit `.streamlit/secrets.toml`, Wi-Fi passwords, tokens or runtime logs to a repository. Caches may retain data in server memory during the process lifetime; a production service needs explicit retention and tenant isolation.

## Optional ESP32 integration guidance — not implemented or tested

Proposed path: calibrated pulse flow meter + pressure transducer → ESP32 → TLS-protected MQTT/HTTPS gateway → timestamped durable store → quality/aggregation job → contract CSV or later authenticated app backend. The current app has **no** MQTT receiver, REST ingestion endpoint or firmware connection. Do not label this path live until hardware, gateway and end-to-end freshness monitoring have been commissioned.

1. Select sensors rated for the installation and local electrical/plumbing requirements. Pressure transducer wiring may require voltage scaling and isolation; follow its datasheet and use competent installation support.
2. Calibrate pulse count against measured volume; store the meter-specific pulses-per-litre factor and uncertainty. Flow L/min = pulse_count / pulses_per_litre / elapsed_minutes. Verify pressure conversion against a known reference. Do not assume a generic calibration constant.
3. Timestamp in UTC after clock synchronization, include device_id, sequence number, interval start/end, quality flags and calibration version. Publish only with individual device credentials; reject replayed sequences and invalid clock skew at the gateway. Buffer outages safely with bounded storage.
4. Aggregate measurements to a continuous 15-minute single-zone series, using duration-weighted mean flow and a documented pressure summary. Confirm timestamps represent the same interval convention as training. Route missing intervals to a quality queue; never replace them with zeros. The current CSV validator requires complete intervals and cannot ingest device metadata directly.
5. Export a de-identified CSV with `timestamp,flow_lpm,pressure_bar`. Train on engineer-verified normal site history. Compare against manual meter checks before enabling operational alerts. Maintain a separate heartbeat/freshness monitor; historical CSV mode cannot detect a disconnected live device.

Proposed gateway payload (illustrative only):

```json
{"device_id":"zone_a_demo","timestamp":"2026-09-21T00:00:00Z","sequence":1234,"flow_lpm":1.2,"pressure_bar":3.1,"quality":"ok","calibration_version":"site-reviewed-v1"}
```

No automatic shutoff is included. Human maintenance decisions and existing site safety procedures remain authoritative.
