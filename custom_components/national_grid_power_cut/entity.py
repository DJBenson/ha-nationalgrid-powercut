"""Shared entity helpers for the National Grid Power Cut integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_POSTCODE, DOMAIN
from .coordinator import NationalGridPowerCutCoordinator


class NationalGridPowerCutEntity(CoordinatorEntity[NationalGridPowerCutCoordinator]):
    """Base entity for National Grid Power Cut entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NationalGridPowerCutCoordinator,
        entry_id: str,
        postcode: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._postcode = postcode
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, postcode)},
            manufacturer="National Grid",
            name=f"National Grid Power Cut {postcode}",
            configuration_url="https://connecteddata.nationalgrid.co.uk/",
        )

    @property
    def base_attributes(self) -> dict[str, Any]:
        """Return attributes common to all entities."""
        return {
            CONF_POSTCODE: self._postcode,
            "total_records": self.coordinator.total,
            "resource_id": self.coordinator.result.get("resource_id"),
            "last_api_query": self.coordinator.result.get("q"),
        }


def compact_record(record: dict[str, Any] | None) -> dict[str, Any]:
    """Return a compact version of a power cut record for attributes."""
    if not record:
        return {}

    useful_keys = (
        "fault_id",
        "status",
        "planned",
        "category",
        "resource_status",
        "licence_area",
        "confirmed_off",
        "predicted_off",
        "restored",
        "planned_outage_off",
        "planned_outage_reason",
        "planned_outage_start_date",
        "planned_outage_end_date",
        "date_of_reported_fault",
        "last_updated",
        "date_of_restoration",
        "date_of_completion",
        "etr",
        "voltage",
        "number_of_psr_customers",
        "number_of_psr_critical_customers",
        "location_latitude",
        "location_longitude",
    )

    return {
        key: value
        for key in useful_keys
        if (value := record.get(key)) not in (None, "")
    }


def compact_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return compact attribute records."""
    return [compact_record(record) for record in records[:10]]
