"""Unit tests for safety blocklist and command verification."""
import tests  # noqa: F401 - installs Home Assistant test stubs
import unittest
from unittest.mock import AsyncMock, MagicMock

# Test safety blocklist from coordinator
from custom_components.staggassistant.coordinator import BLOCKED_COMMANDS, StaggLinkCoordinator


class TestKettleSafety(unittest.IsolatedAsyncioTestCase):
    """Ensure dangerous direct GPIO and wipe commands are blocked."""

    def setUp(self):
        self.mock_hass = MagicMock()
        self.coordinator = StaggLinkCoordinator(self.mock_hass, "192.168.1.100", 15)

    async def test_blocked_dangerous_commands(self):
        """Verify that direct hardware heater commands and wipe commands raise an error."""
        from homeassistant.exceptions import HomeAssistantError

        dangerous_samples = [
            "heaton",
            "HEATON",
            "heatoff",
            "warmon",
            "warmoff",
            "warmduty 50",
            "gpioset 12 1",
            "reset",
            "clrsettings",
            "wifierase",
            "wifioff",
            "provreset",
            "eraseotherpart",
            "adcsamples",
            "ss",  # bare ss crashes/reboots kettle
            "  ss  ",
        ]

        for cmd in dangerous_samples:
            with self.subTest(cmd=cmd):
                with self.assertRaises(HomeAssistantError):
                    await self.coordinator.async_send_command(cmd)

    async def test_allowed_safe_commands(self):
        """Verify that legitimate state machine commands pass the safety guard."""
        # Mock session.get context manager
        mock_response = AsyncMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.text = AsyncMock(return_value="OK")

        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_response

        self.coordinator.session.get = MagicMock(return_value=mock_cm)

        safe_samples = [
            "ss S_Heat",
            "ss S_Off",
            "ss S_Hold",
            "setsetting settempr 185",
            "setsetting schtempr 190",
            "setsetting hold 30",
            "setsetting boil 1",
            "setdigital",
            "setanalog",
            "setunitsc",
            "setunitsf",
            "setaltitudem 500",
            "2",
            "1",
            "q",
            "w",
            "2d",
            "2u",
            "setclock 12 30 0",
        ]

        for cmd in safe_samples:
            with self.subTest(cmd=cmd):
                result = await self.coordinator.async_send_command(cmd)
                self.assertEqual(result, "OK")


if __name__ == "__main__":
    unittest.main()
