"""Binary sensor platform for the National Grid Power Cut integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_POSTCODE
from .coordinator import NationalGridPowerCutCoordinator
from .entity import NationalGridPowerCutEntity, compact_record, compact_records


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[NationalGridPowerCutCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up National Grid Power Cut binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        [
            NationalGridPowerCutReportedBinarySensor(
                coordinator, entry.entry_id, entry.data[CONF_POSTCODE]
            )
        ]
    )


class NationalGridPowerCutReportedBinarySensor(
    NationalGridPowerCutEntity, BinarySensorEntity
):
    """Binary sensor indicating whether a power cut is reported."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:transmission-tower-off"
    _attr_name = "Power cut reported"
    _attr_translation_key = "power_cut_reported"

    def __init__(
        self,
        coordinator: NationalGridPowerCutCoordinator,
        entry_id: str,
        postcode: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id, postcode)
        self._attr_unique_id = f"{entry_id}_power_cut_reported"

    @property
    def is_on(self) -> bool:
        """Return whether a power cut is reported."""
        return self.coordinator.power_cut_reported

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return useful outage details as attributes."""
        return {
            **self.base_attributes,
            "primary_incident": compact_record(self.coordinator.primary_record),
            "incidents": compact_records(self.coordinator.records),
        }
