"""Support for Fellow Stagg EKG Pro climate entity."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import StaggLinkCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up StaggLink climate platform."""
    coordinator: StaggLinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([StaggKettleClimate(coordinator, entry)], True)


class StaggKettleClimate(CoordinatorEntity[StaggLinkCoordinator], ClimateEntity):
    """Representation of a Stagg EKG Pro Kettle as a climate entity."""

    def __init__(self, coordinator: StaggLinkCoordinator, entry):
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._ip = entry.data["ip_address"]
        device_name = entry.data.get("name", "Stagg Kettle")
        device_id = f"stagglink_{self._ip.replace('.', '_')}"

        # Primary entity of the device uses name = None with has_entity_name = True
        self._attr_has_entity_name = True
        self._attr_name = None
        self._attr_unique_id = device_id

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Fellow",
            model="Stagg EKG Pro",
            configuration_url=f"http://{self._ip}",
        )

        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_target_temperature_step = 0.5

        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        self._attr_min_temp = 40
        self._attr_max_temp = 100

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if not self.coordinator.data:
            return HVACMode.OFF
        return HVACMode.OFF if self.coordinator.data.get("mode") == "S_Off" else HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
        """Return the current running hvac operation."""
        if not self.coordinator.data:
            return HVACAction.OFF
        mode = self.coordinator.data.get("mode", "S_Off")
        if mode == "S_Off":
            return HVACAction.OFF
        if "High" in mode or "Heat" in mode or mode == "S_StartupToTempr":
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def icon(self) -> str:
        """Return dynamic icon based on state."""
        if self.hvac_action == HVACAction.HEATING:
            return "mdi:kettle-steam"
        return "mdi:kettle"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        if self.coordinator.data:
            return self.coordinator.data.get("temp")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target set temperature."""
        if self.coordinator.data:
            return self.coordinator.data.get("target")
        return None

    async def async_turn_on(self) -> None:
        """Turn the kettle heating on."""
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        """Turn the kettle off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.async_send_command("ss S_Off")
        elif hvac_mode == HVACMode.HEAT:
            await self.coordinator.async_send_command("ss S_Heat")

        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            # Clamp to valid operating range
            clamped_c = max(self._attr_min_temp, min(self._attr_max_temp, float(temp)))
            # Convert Celsius to Fahrenheit with proper rounding for precision
            fahrenheit = round(clamped_c * 1.8 + 32)

            # 1. Send temperature target
            await self.coordinator.async_send_command(f"setsetting settempr {fahrenheit}")

            # 2. Ensure kettle transitions to heating mode
            await self.coordinator.async_send_command("ss S_Heat")

            await self.coordinator.async_request_refresh()
