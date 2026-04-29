"""National Grid Power Cut integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NationalGridPowerCutClient
from .const import (
    CONF_POSTCODE,
    CONF_SCAN_INTERVAL_MINUTES,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    MAX_SCAN_INTERVAL_MINUTES,
    MIN_SCAN_INTERVAL_MINUTES,
)
from .coordinator import NationalGridPowerCutCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


def _get_scan_interval_minutes(entry: ConfigEntry) -> int:
    """Return a valid scan interval from entry options or data."""
    value = entry.options.get(
        CONF_SCAN_INTERVAL_MINUTES,
        entry.data.get(CONF_SCAN_INTERVAL_MINUTES, DEFAULT_SCAN_INTERVAL_MINUTES),
    )

    try:
        minutes = int(float(value))
    except (TypeError, ValueError):
        minutes = DEFAULT_SCAN_INTERVAL_MINUTES

    return min(max(minutes, MIN_SCAN_INTERVAL_MINUTES), MAX_SCAN_INTERVAL_MINUTES)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up National Grid Power Cut from a config entry."""
    session = async_get_clientsession(hass)
    client = NationalGridPowerCutClient(session, entry.data[CONF_POSTCODE])
    coordinator = NationalGridPowerCutCoordinator(
        hass,
        client,
        _get_scan_interval_minutes(entry),
    )

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
