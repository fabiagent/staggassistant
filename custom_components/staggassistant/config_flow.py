"""Config flow and options flow for Fellow Stagg EKG Pro integration."""
import asyncio
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class StaggAssistantConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for StaggAssistant."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}
        if user_input is not None:
            ip = user_input[CONF_IP_ADDRESS].strip()

            # Guard against duplicate entries for the same device IP
            await self.async_set_unique_id(ip)
            self._abort_if_unique_id_configured()

            session = async_get_clientsession(self.hass)
            url = f"http://{ip}/cli"
            try:
                async with asyncio.timeout(5):
                    async with session.get(url, params={"cmd": "state"}) as response:
                        if response.status == 200:
                            text = await response.text()
                            if "mode=" in text or "tempr=" in text:
                                return self.async_create_entry(
                                    title=user_input.get(CONF_NAME, "Stagg Kettle"),
                                    data=user_input,
                                )
                            errors["base"] = "invalid_auth"
                        else:
                            errors["base"] = "cannot_connect"
            except (asyncio.TimeoutError, Exception):
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_NAME, default="Stagg Kettle"): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=120)
                ),
            }),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return StaggAssistantOptionsFlow(config_entry)


class StaggAssistantOptionsFlow(config_entries.OptionsFlow):
    """Handle StaggAssistant options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage integration options (e.g. polling interval)."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=120)
                ),
            }),
        )
