"""Sensor platform for the National Grid Power Cut integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_POSTCODE
from .coordinator import NationalGridPowerCutCoordinator
from .entity import NationalGridPowerCutEntity, compact_record, compact_records


@dataclass(frozen=True, kw_only=True)
class NationalGridPowerCutSensorEntityDescription(SensorEntityDescription):
    """Description for National Grid Power Cut sensors."""

    value_fn: Callable[[NationalGridPowerCutCoordinator], Any]
    attributes_fn: Callable[[NationalGridPowerCutCoordinator], dict[str, Any]] | None = None


def _parse_datetime(value: Any) -> datetime | None:
    """Parse API timestamps for timestamp sensors."""
    if not isinstance(value, str) or not value:
        return None

    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)

    return parsed


def _primary_status(coordinator: NationalGridPowerCutCoordinator) -> str:
    """Return the current primary incident status."""
    record = coordinator.primary_record
    if not record:
        return "No power cut reported"

    return record.get("status") or "Power cut reported"


def _primary_etr(coordinator: NationalGridPowerCutCoordinator) -> datetime | None:
    """Return the primary estimated restoration time."""
    record = coordinator.primary_record
    if not record:
        return None

    return _parse_datetime(record.get("etr"))


def _planned_start(coordinator: NationalGridPowerCutCoordinator) -> datetime | None:
    """Return the next planned outage start timestamp."""
    record = _planned_record(coordinator)
    if not record:
        return None

    return _parse_datetime(record.get("planned_outage_start_date"))


def _planned_record(
    coordinator: NationalGridPowerCutCoordinator,
) -> dict[str, Any] | None:
    """Return the first record that looks like a planned outage."""
    for record in coordinator.records:
        planned_value = str(record.get("planned", "")).lower()
        if planned_value in {"yes", "true", "1", "planned"} or record.get(
            "planned_outage_start_date"
        ):
            return record

    return None


SENSORS: tuple[NationalGridPowerCutSensorEntityDescription, ...] = (
    NationalGridPowerCutSensorEntityDescription(
        key="incident_count",
        translation_key="incident_count",
        native_unit_of_measurement="incidents",
        icon="mdi:counter",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda coordinator: coordinator.total,
        attributes_fn=lambda coordinator: {
            "incidents": compact_records(coordinator.records),
        },
    ),
    NationalGridPowerCutSensorEntityDescription(
        key="status",
        translation_key="status",
        icon="mdi:transmission-tower",
        value_fn=_primary_status,
        attributes_fn=lambda coordinator: compact_record(coordinator.primary_record),
    ),
    NationalGridPowerCutSensorEntityDescription(
        key="estimated_restoration_time",
        translation_key="estimated_restoration_time",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-alert-outline",
        value_fn=_primary_etr,
        attributes_fn=lambda coordinator: {
            key: value
            for key in (
                "date_of_restoration",
                "date_of_completion",
                "last_updated",
            )
            if coordinator.primary_record
            and (value := coordinator.primary_record.get(key)) not in (None, "")
        },
    ),
    NationalGridPowerCutSensorEntityDescription(
        key="planned_outage_start",
        translation_key="planned_outage_start",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:calendar-alert",
        value_fn=_planned_start,
        attributes_fn=lambda coordinator: {
            key: value
            for key in (
                "planned_outage_end_date",
                "planned_outage_off",
                "planned_outage_reason",
            )
            if _planned_record(coordinator)
            and (value := _planned_record(coordinator).get(key)) not in (None, "")
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry[NationalGridPowerCutCoordinator],
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up National Grid Power Cut sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        NationalGridPowerCutSensor(
            coordinator,
            entry.entry_id,
            entry.data[CONF_POSTCODE],
            description,
        )
        for description in SENSORS
    )


class NationalGridPowerCutSensor(NationalGridPowerCutEntity, SensorEntity):
    """Sensor backed by National Grid power cut API data."""

    entity_description: NationalGridPowerCutSensorEntityDescription

    def __init__(
        self,
        coordinator: NationalGridPowerCutCoordinator,
        entry_id: str,
        postcode: str,
        description: NationalGridPowerCutSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry_id, postcode)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return sensor-specific attributes."""
        attributes = dict(self.base_attributes)
        if self.entity_description.attributes_fn:
            attributes.update(self.entity_description.attributes_fn(self.coordinator))

        return attributes
