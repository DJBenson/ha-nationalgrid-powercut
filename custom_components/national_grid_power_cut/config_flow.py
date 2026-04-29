"""Config flow for the National Grid Power Cut integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    CannotConnectError,
    InvalidPostcodeError,
    InvalidResponseError,
    NationalGridPowerCutClient,
    normalize_postcode,
)
from .const import CONF_POSTCODE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class NationalGridPowerCutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for National Grid Power Cut."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                postcode = normalize_postcode(user_input[CONF_POSTCODE])
                await self._async_validate_postcode(postcode)
            except InvalidPostcodeError:
                errors["base"] = "invalid_postcode"
            except CannotConnectError:
                errors["base"] = "cannot_connect"
            except InvalidResponseError:
                errors["base"] = "invalid_response"
            except Exception:
                _LOGGER.exception("Unexpected exception validating postcode")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(postcode)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"National Grid Power Cut ({postcode})",
                    data={CONF_POSTCODE: postcode},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_POSTCODE): str,
                }
            ),
            errors=errors,
        )

    async def _async_validate_postcode(self, postcode: str) -> None:
        """Validate that the API accepts the configured postcode."""
        session = async_get_clientsession(self.hass)
        client = NationalGridPowerCutClient(session, postcode)
        await client.async_get_power_cuts()
