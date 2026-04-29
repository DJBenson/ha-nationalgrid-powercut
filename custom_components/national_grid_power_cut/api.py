"""Client for the National Grid connected data API."""

from __future__ import annotations

import asyncio
import re
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

from .const import API_URL, RESOURCE_ID

POSTCODE_RE = re.compile(r"^[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}$")


class NationalGridPowerCutError(Exception):
    """Base error for the National Grid Power Cut API."""


class InvalidPostcodeError(NationalGridPowerCutError):
    """Raised when a postcode is not valid enough to query."""


class CannotConnectError(NationalGridPowerCutError):
    """Raised when the API cannot be reached."""


class InvalidResponseError(NationalGridPowerCutError):
    """Raised when the API returns an unexpected response."""


def normalize_postcode(postcode: str) -> str:
    """Normalize a UK postcode for storage and API queries."""
    compact = re.sub(r"\s+", "", postcode or "").upper()
    if not POSTCODE_RE.fullmatch(compact):
        raise InvalidPostcodeError("Invalid UK postcode")

    return f"{compact[:-3]} {compact[-3:]}"


class NationalGridPowerCutClient:
    """Small async client for the National Grid power cut datastore."""

    def __init__(self, session: ClientSession, postcode: str) -> None:
        """Initialize the client."""
        self._session = session
        self.postcode = normalize_postcode(postcode)

    async def async_get_power_cuts(self) -> dict[str, Any]:
        """Retrieve live power cut data for the configured postcode."""
        params = {
            "resource_id": RESOURCE_ID,
            "q": self.postcode,
        }

        try:
            async with asyncio.timeout(20):
                response = await self._session.get(API_URL, params=params)
                response.raise_for_status()
                data: dict[str, Any] = await response.json()
        except (TimeoutError, ClientResponseError, ClientError) as err:
            raise CannotConnectError from err

        if not data.get("success"):
            raise InvalidResponseError("National Grid API returned success=false")

        result = data.get("result")
        if not isinstance(result, dict):
            raise InvalidResponseError("National Grid API response did not include result")

        records = result.get("records")
        if not isinstance(records, list):
            raise InvalidResponseError("National Grid API response did not include records")

        return data
