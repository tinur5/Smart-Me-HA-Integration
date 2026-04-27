# Smart-Me Local – Home Assistant Integration

A **custom Home Assistant integration** that connects directly to your
[Smart-Me](https://smart-me.com) smart meter over your **local network**,
without requiring any cloud account or internet access.

---

## Features

| Sensor | Unit | Default enabled |
|---|---|---|
| Active Power (total) | W | ✅ |
| Active Power L1 / L2 / L3 | W | disabled |
| Voltage (total) | V | ✅ |
| Voltage L1 / L2 / L3 | V | disabled |
| Current (total) | A | ✅ |
| Current L1 / L2 / L3 | A | disabled |
| Energy – Total (counter reading) | kWh | ✅ |
| Energy – Import | kWh | disabled |
| Energy – Export | kWh | disabled |
| Frequency | Hz | disabled |
| Power Factor | – | disabled |

All disabled sensors can be enabled from the Home Assistant entity settings
after installation.

---

## Requirements

* Home Assistant **2024.1** or later (any recent version with `config_entries`
  v2 support will work)
* A **Smart-Me** device accessible on your local network  
  (tested with Smart-Me Wi-Fi energy meter and Smart-Me cloud gateway)

---

## Installation

### Option A – HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → *Custom repositories*.
2. Add `https://github.com/tinur5/Smart-Me-HA-Integration` as an
   **Integration** category.
3. Search for **Smart-Me Local** and click *Download*.
4. Restart Home Assistant.

### Option B – Manual

1. Download or clone this repository.
2. Copy the `custom_components/smart_me_local/` folder into your Home
   Assistant configuration directory:
   ```
   <config>/custom_components/smart_me_local/
   ```
3. Restart Home Assistant.

---

## Configuration

1. Navigate to **Settings → Devices & Services → Add Integration**.
2. Search for **Smart-Me Local**.
3. Fill in the form:

| Field | Description |
|---|---|
| **Device IP address or hostname** | The local IP / hostname of your Smart-Me device (e.g. `192.168.1.100`). |
| **Device serial number (username)** | The device serial number – used as the HTTP Basic Auth username. |
| **Device password** | The device password (factory default is `0000`). |

4. Click **Submit**. Home Assistant connects to the device and creates all
   sensor entities automatically.

---

## Local API

This integration talks directly to the device's built-in REST API:

```
GET http://<device-ip>/api/device
Authorization: Basic <base64(serial:password)>
```

**Example response (shortened):**

```json
{
  "Id": "12345678-abcd-...",
  "Name": "My Smart Meter",
  "Serial": "SN12345678",
  "ActivePower": 1.536,
  "ActivePowerL1": 0.612,
  "ActivePowerL2": 0.502,
  "ActivePowerL3": 0.422,
  "Voltage": 230.1,
  "VoltageL1": 230.1,
  "VoltageL2": 229.8,
  "VoltageL3": 230.4,
  "Current": 6.52,
  "CurrentL1": 2.60,
  "CurrentL2": 2.17,
  "CurrentL3": 1.74,
  "CounterReading": 1234.567,
  "CounterReadingImport": 1234.567,
  "CounterReadingExport": 0.000,
  "Frequency": 50.02,
  "PowerFactor": 0.998
}
```

> **Tip**: Point your browser to `http://<device-ip>/api/device` (using your
> browser's Basic-Auth dialog or a tool like [HTTPie](https://httpie.io/)) to
> inspect the raw response from your specific device.

---

## Project Structure

```
custom_components/smart_me_local/
├── __init__.py          # Integration setup / teardown
├── api.py               # Async HTTP client for the local device API
├── config_flow.py       # UI configuration flow
├── const.py             # Integration constants
├── coordinator.py       # DataUpdateCoordinator (polls every 10 s)
├── manifest.json        # Integration metadata
├── sensor.py            # Sensor entity platform
├── strings.json         # UI strings (source-of-truth for translations)
└── translations/
    └── en.json          # English translations
tests/
├── conftest.py          # Shared test fixtures
├── test_api.py          # Unit tests for the API client
├── test_config_flow.py  # Unit tests for the config flow
└── test_sensor.py       # Unit tests for sensor value functions
```

---

## Development

### Prerequisites

```bash
pip install pytest pytest-asyncio aiohttp homeassistant
```

### Running tests

```bash
pytest tests/
```

---

## API Documentation

* **Local device REST API (Swagger):**  
  `https://api.smart-me.com/swagger/index.html`
* **Official Smart-Me documentation:**  
  `https://dok.smart-me.com/home`

---

## Changelog

### 1.0.0 (initial release)
* Local-network polling of the Smart-Me REST API (no cloud required).
* Sensors: Active Power, Voltage, Current, Energy, Frequency, Power Factor.
* UI-based configuration flow with connection validation.
* Fully async implementation; updates every 10 seconds.

---

## License

MIT – see [LICENSE](LICENSE) for details.