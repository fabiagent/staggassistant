<img src="icon.png" align="top-left" width="140" alt="StaggAssistant Logo" style="margin-right: 20px; padding-bottom: 20px;">

# StaggAssistant 🦢☕️

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/fabiagent/staggassistant)](https://github.com/fabiagent/staggassistant/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant integration for the **Fellow Stagg EKG Pro** kettle.
This integration communicates directly with the kettle's internal **CLI wrapper** over local HTTP.

> [!NOTE]
> **🤖 AI-Maintained Fork:** This repository is an enhanced fork of the original [`fabiankirchen/staggassistant`](https://github.com/fabiankirchen/staggassistant), maintained and evolved autonomously by **`fabiagent`** (AI Agent) on behalf of [@fabiankirchen](https://github.com/fabiankirchen). All changes are covered by automated unit test suites and hardware safety guards.

<br clear="left"/>

## ✨ Features

* **Direct CLI Communication:** Sends commands directly to the device's internal interface (e.g., `ss S_Heat`, `settempr`).
* **Built-in Safety Blocklist:** Strictly blocks dangerous commands (`heaton`, `heatoff`, `warmon`, `warmoff`, `gpioset`, `reset`) that bypass firmware safety logic and dry-boil protections.
* **Precision Control:** Supports 0.5°C steps with accurate rounding for target temperature.
* **Full Remote Control:** Brings the kettle's hardware features straight into Home Assistant, allowing you to comfortably manage settings, clock display, and schedules remotely.
* **Configurable:** Adjust the update interval during setup or anytime later via Options (default: 15s).

## 📋 Available Entities & Controls

The integration exposes **27 entities** to fully monitor and manage your kettle from Home Assistant:

| Platform | Entity | Description |
| :--- | :--- | :--- |
| **`climate`** | Kettle Controller | Main thermostat UI to turn on/off and set temperature |
| **`sensor`** | Current Temperature | Current water temperature (with statistics history) |
| **`sensor`** | Target Temperature | Target set temperature |
| **`sensor`** | Boil Temperature | Altitude-adjusted boiling temperature |
| **`sensor`** | State Mode | Human-readable kettle state (Off, Heat, Hold, etc.) |
| **`sensor`** | Clock Time | Current kettle clock time |
| **`sensor`** | Schedule Time | Scheduled wake-up time (HH:MM) |
| **`sensor`** | Schedule Temperature | Scheduled target temperature |
| **`binary_sensor`** | Docked | Detects if the kettle is resting on the base |
| **`binary_sensor`** | Low Water Warning | Dry-boil / low-water alert (`nw` flag) |
| **`binary_sensor`** | Target Temperature Reached | Signals when water has reached the desired temperature |
| **`binary_sensor`** | Pre-Boil Active | Signals when pre-boil heating is actively running |
| **`binary_sensor`** | Heating Active | Indicates heating element operation |
| **`binary_sensor`** | Hold Active | Indicates keep-warm mode is actively maintaining temperature |
| **`switch`** | Pre-Boil | Toggle the pre-boil feature on/off |
| **`number`** | Hold Time Duration | Set hold time duration in minutes (0–60) |
| **`number`** | Altitude Setting | Set altitude for boil calibration (0–3000 m) |
| **`number`** | Chime Volume | Set chime volume (0–10) |
| **`number`** | Schedule Temperature | Set scheduled target temperature |
| **`select`** | Clock Style | Choose off, digital, or analog clock display |
| **`select`** | Language Selection | Supports all 7 internal languages (EN, FR, ES, ZH-Hans, ZH-Hant, KO, JA) |
| **`select`** | Temperature Units | Switch display units between Celsius and Fahrenheit |
| **`select`** | Schedule Mode | Choose off, once, or repeat schedule |
| **`button`** | Press Main Button | Simulate pressing the main dial button (e.g., starts a brew timer) |
| **`button`** | Press Menu Button | Simulate pressing the back/menu button |
| **`button`** | Rotate Dial Left | Rotate the dial counter-clockwise |
| **`button`** | Rotate Dial Right | Rotate the dial clockwise |
| **`button`** | Start Timer | Long press dial button to start brew timer |
| **`button`** | Sync Time | Sync current Home Assistant system time to the kettle |
| **`button`** | Reload Data | Force a manual data refresh from the kettle |

## 🚀 Installation

### Option 1: HACS (Recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** > Top right menu (**⋮**) > **Custom repositories**.
3. Add the URL of this repository: `https://github.com/fabiagent/staggassistant`
4. Category: **Integration**.
5. Click **Add**, then search for "StaggAssistant" in the list and install it.
6. Restart Home Assistant.

### Option 2: Manual

1. Download the latest release from the [Releases section](https://github.com/fabiagent/staggassistant/releases).
2. Unzip the file.
3. Copy the `custom_components/staggassistant` folder into your Home Assistant `/config/custom_components/` directory (so that the path is `/config/custom_components/staggassistant`).
4. Restart Home Assistant.

## ⚙️ Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **StaggAssistant**.
4. Enter the **IP address** of your kettle and choose your preferred update interval.
5. (Optional) To adjust settings later, click **Configure / Options** on the integration card.

## 🤖 Disclaimer & AI Maintenance

This integration is an unofficial community project and is not affiliated with Fellow Industries, Inc.
This fork is autonomously maintained, tested, and updated by **`fabiagent`** on behalf of Fabian Kirchen. Use at your own risk.

## ❤️ Credits

* Original repository: **[fabiankirchen/staggassistant](https://github.com/fabiankirchen/staggassistant)**
* Big thanks to the repositories **[stagg-ekg-pro](https://github.com/tomtastic/stagg-ekg-pro)** & **[homebridge-kettle](https://github.com/Willmac16/homebridge-kettle/tree/ekg-pro-cli)** through which I discovered how to communicate with the kettle.
* A huge shout-out and massive thanks to **[@miguelcaravantes](https://github.com/miguelcaravantes)** for contributing the entire multi-platform overhaul, unlocking the scheduling features, dial buttons, and lifting this integration to a whole new level!

## 📄 License

MIT License. See [LICENSE](LICENSE) file for more details.
This project is not affiliated with Fellow Industries, Inc.
