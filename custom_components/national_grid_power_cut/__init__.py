"""National Grid Power Cut integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NationalGridPowerCutClient
from .const import CONF_POSTCODE, DOMAIN
from .coordinator import NationalGridPowerCutCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up National Grid Power Cut from a config entry."""
    session = async_get_clientsession(hass)
    client = NationalGridPowerCutClient(session, entry.data[CONF_POSTCODE])
    coordinator = NationalGridPowerCutCoordinator(hass, client)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
