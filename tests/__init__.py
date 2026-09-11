"""Mock minimal Home Assistant modules for standalone unit testing."""
import sys
from unittest.mock import MagicMock


class MockHomeAssistantError(Exception):
    pass


class MockUpdateFailed(Exception):
    pass


class MockDataUpdateCoordinator:
    def __init__(self, hass, logger, name, update_interval):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None

    async def async_request_refresh(self):
        pass


class MockDeviceInfo(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


# Install mock aiohttp if not present
if "aiohttp" not in sys.modules:
    aiohttp_mock = MagicMock()

    class MockClientError(Exception):
        pass

    aiohttp_mock.ClientError = MockClientError
    sys.modules["aiohttp"] = aiohttp_mock

# Install mock homeassistant packages into sys.modules if not already present
if "homeassistant" not in sys.modules:
    ha = MagicMock()
    sys.modules["homeassistant"] = ha

    ha_exceptions = MagicMock()
    ha_exceptions.HomeAssistantError = MockHomeAssistantError
    sys.modules["homeassistant.exceptions"] = ha_exceptions

    ha_coordinator = MagicMock()
    ha_coordinator.DataUpdateCoordinator = MockDataUpdateCoordinator
    ha_coordinator.UpdateFailed = MockUpdateFailed
    sys.modules["homeassistant.helpers.update_coordinator"] = ha_coordinator

    ha_aiohttp = MagicMock()
    ha_aiohttp.async_get_clientsession = lambda hass: MagicMock()
    sys.modules["homeassistant.helpers.aiohttp_client"] = ha_aiohttp

    ha_device_reg = MagicMock()
    ha_device_reg.DeviceInfo = MockDeviceInfo
    sys.modules["homeassistant.helpers.device_registry"] = ha_device_reg

    ha_entries = MagicMock()
    ha_entries.ConfigEntry = MagicMock
    ha_entries.ConfigFlow = MagicMock
    ha_entries.OptionsFlow = MagicMock
    sys.modules["homeassistant.config_entries"] = ha_entries

    ha_core = MagicMock()
    ha_core.HomeAssistant = MagicMock
    ha_core.callback = lambda f: f
    sys.modules["homeassistant.core"] = ha_core

    ha_const = MagicMock()
    ha_const.ATTR_TEMPERATURE = "temperature"

    class MockUnitOfTemperature:
        CELSIUS = "°C"
        FAHRENHEIT = "°F"

    ha_const.UnitOfTemperature = MockUnitOfTemperature
    sys.modules["homeassistant.const"] = ha_const

    ha_climate = MagicMock()
    sys.modules["homeassistant.components.climate"] = ha_climate
    sys.modules["homeassistant.components.climate.const"] = MagicMock()

    ha_sensor = MagicMock()
    sys.modules["homeassistant.components.sensor"] = ha_sensor

    ha_bsensor = MagicMock()
    sys.modules["homeassistant.components.binary_sensor"] = ha_bsensor

    ha_number = MagicMock()
    sys.modules["homeassistant.components.number"] = ha_number

    ha_select = MagicMock()
    sys.modules["homeassistant.components.select"] = ha_select

    ha_switch = MagicMock()
    sys.modules["homeassistant.components.switch"] = ha_switch

    ha_button = MagicMock()
    sys.modules["homeassistant.components.button"] = ha_button

    sys.modules["homeassistant.util.dt"] = MagicMock()
