"""Data update coordinator for the National Grid Power Cut integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NationalGridPowerCutClient, NationalGridPowerCutError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class NationalGridPowerCutCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate National Grid power cut API updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: NationalGridPowerCutClient,
        scan_interval_minutes: int,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=scan_interval_minutes),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the latest API data."""
        try:
            return await self.client.async_get_power_cuts()
        except NationalGridPowerCutError as err:
            raise UpdateFailed(str(err)) from err

    @property
    def result(self) -> dict[str, Any]:
        """Return the API result object."""
        return self.data.get("result", {}) if self.data else {}

    @property
    def records(self) -> list[dict[str, Any]]:
        """Return outage records."""
        records = self.result.get("records", [])
        return records if isinstance(records, list) else []

    @property
    def total(self) -> int:
        """Return the total matching record count."""
        total = self.result.get("total")
        return total if isinstance(total, int) else len(self.records)

    @property
    def primary_record(self) -> dict[str, Any] | None:
        """Return the most relevant matching record."""
        if not self.records:
            return None

        return self.records[0]

    @property
    def power_cut_reported(self) -> bool:
        """Return whether the API has any matching live records."""
        return self.total > 0
