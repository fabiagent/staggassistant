"""DataUpdateCoordinator for Fellow Stagg EKG Pro integration."""
import asyncio
import logging
import re
from datetime import timedelta
import aiohttp

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

# Dangerous commands that bypass firmware safety, drive raw GPIOs, or wipe settings
BLOCKED_COMMANDS = {
    "heaton",
    "heatoff",
    "warmon",
    "warmoff",
    "warmduty",
    "gpioset",
    "reset",
    "clrsettings",
    "wifierase",
    "wifioff",
    "provreset",
    "eraseotherpart",
    "adcsamples",
}


class StaggLinkCoordinator(DataUpdateCoordinator):
    """Central instance to fetch data from and send commands to the kettle CLI API."""

    def __init__(self, hass, ip, update_interval_seconds):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="StaggLink Kettle",
            update_interval=timedelta(seconds=update_interval_seconds),
        )
        self.ip = ip
        self.session = async_get_clientsession(hass)

    async def async_send_command(self, cmd: str) -> str:
        """Send a CLI command safely to the kettle.

        Guards against raw GPIO heater activation or destructive commands.
        """
        clean_cmd = cmd.strip()
        first_word = clean_cmd.split()[0].lower() if clean_cmd else ""

        if first_word in BLOCKED_COMMANDS or clean_cmd.lower() == "ss":
            _LOGGER.error("Blocked potentially dangerous command: '%s'", clean_cmd)
            raise HomeAssistantError(f"Command '{clean_cmd}' is blocked for safety.")

        url = f"http://{self.ip}/cli"
        try:
            async with asyncio.timeout(10):
                async with self.session.get(url, params={"cmd": clean_cmd}) as response:
                    response.raise_for_status()
                    return await response.text()
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout sending command '%s' to %s", clean_cmd, self.ip)
            raise HomeAssistantError(f"Timeout communicating with Stagg kettle at {self.ip}") from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error sending command '%s' to %s: %s", clean_cmd, self.ip, err)
            raise HomeAssistantError(f"Error communicating with Stagg kettle: {err}") from err

    async def _async_update_data(self):
        """Fetch data from the kettle via HTTP CLI commands."""
        state_url = f"http://{self.ip}/cli"

        try:
            async with asyncio.timeout(15):
                # 1. Fetch current device state
                async with self.session.get(state_url, params={"cmd": "state"}) as response:
                    response.raise_for_status()
                    state_text = await response.text()

                # 2. Fetch system settings dump
                async with self.session.get(state_url, params={"cmd": "prtsettings"}) as response_settings:
                    response_settings.raise_for_status()
                    settings_text = await response_settings.text()

                # Parse temperature values (negative lookahead avoids matching temprT / temprB as tempr)
                temp_match = re.search(r'\btempr(?![TB])\s*=\s*(-?[0-9.]+|nan)', state_text)
                target_match = re.search(r'\btemprT\s*=\s*(-?[0-9.]+|nan)', state_text)
                boil_match = re.search(r'\btemprB\s*=\s*(-?[0-9.]+|nan)', state_text)
                mode_match = re.search(r'\bmode\s*=\s*([a-zA-Z0-9_+]+)', state_text)

                if not temp_match or not target_match or not mode_match:
                    raise UpdateFailed(f"Parsing error. Incomplete response: {state_text}")

                def parse_float(value):
                    if value is None or value == 'nan':
                        return None
                    try:
                        return float(value)
                    except ValueError:
                        return None

                def get_setting_value(name, default=None):
                    match = re.search(rf'\b{name}\s*[:=]\s*([a-zA-Z0-9_.-]+)', settings_text, re.IGNORECASE)
                    if match:
                        val = match.group(1).strip()
                        try:
                            if '.' in val:
                                return float(val)
                            return int(val)
                        except ValueError:
                            return val
                    return default

                def get_time_value(name, default=None):
                    """Parse HH:MM values."""
                    match = re.search(rf'\b{name}\s*=\s*([0-9]+:[0-9]+)', settings_text, re.IGNORECASE)
                    return match.group(1) if match else default

                # Parse clock time directly from state_text (eliminates 1 HTTP call per poll)
                clock_time = None
                clock_match = re.search(r'\bclock\s*=\s*([0-9]+:[0-9]+)', state_text)
                if clock_match:
                    try:
                        h, m = clock_match.group(1).split(":")
                        clock_time = f"{int(h):02d}:{int(m):02d}"
                    except Exception:
                        clock_time = clock_match.group(1)

                # Parse ketl= line flags (e.g. "ketl= ho 0 wd 0 nw 0 ipb 0 bf 0 tr 0")
                ketl_match = re.search(r'\bketl\s*=\s*(.*)$', state_text, re.MULTILINE)
                flags = {}
                if ketl_match:
                    flags = dict(re.findall(r'([a-zA-Z]+)\s+([0-9]+)', ketl_match.group(1)))

                no_water = flags.get("nw") == "1"
                target_reached = flags.get("tr") == "1"
                in_pre_boil = flags.get("ipb") == "1"
                hold_flag = flags.get("ho") == "1"

                current_temp = parse_float(temp_match.group(1))
                target_temp = parse_float(target_match.group(1))
                boil_temp = parse_float(boil_match.group(1)) if boil_match else None

                # When kettle is off the base, tempr reports 'nan'
                is_docked = current_temp is not None

                # Schedule temperature: "schtempr=N F (X C ...)" or "schtempr=N C (X C ...)"
                sch_tempr_c = None
                sch_match = re.search(r'schtempr\s*=\s*.*?\s*(-?[0-9.]+)\s*C', settings_text)
                if sch_match:
                    try:
                        sch_tempr_c = float(sch_match.group(1))
                    except ValueError:
                        pass

                schedon = get_setting_value("schedon", 0)
                repeat_sched = get_setting_value("Repeat_sched", 0)
                if schedon == 0:
                    schedule_mode = "off"
                    sch_tempr_c = None  # Hide temperature if schedule is off
                elif repeat_sched:
                    schedule_mode = "repeat"
                else:
                    schedule_mode = "once"

                return {
                    "temp": current_temp,
                    "target": target_temp,
                    "boil_temp": boil_temp,
                    "mode": mode_match.group(1),
                    "is_docked": is_docked,
                    "no_water": no_water,
                    "target_reached": target_reached,
                    "in_pre_boil": in_pre_boil,
                    "hold_flag": hold_flag,
                    "hold_time_minutes": get_setting_value("hold", 30),
                    "hold_enabled": 1 if get_setting_value("hold", 0) > 0 else 0,
                    "pre_boil_enabled": get_setting_value("boil", 0),
                    "chime_enabled": 1 if get_setting_value("chime", 0) > 0 else 0,
                    "chime_volume": get_setting_value("chime", 0),
                    "altitude_meters": get_setting_value("altitude", 0),
                    "language": get_setting_value("language", 0),
                    "units": "C" if get_setting_value("units", 1) == 1 else "F",
                    "clock_mode": get_setting_value("clockmode", 0),
                    "clock_time": clock_time,
                    "schedule_enabled": schedon,
                    "schedule_mode": schedule_mode,
                    "schedule_time": get_time_value("schtime"),
                    "schedule_temperature": sch_tempr_c,
                }

        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Connection error: {err}") from err
