"""Config flow for the National Grid Power Cut integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .api import (
    CannotConnectError,
    InvalidPostcodeError,
    InvalidResponseError,
    NationalGridPowerCutClient,
    normalize_postcode,
)
from .const import (
    CONF_POSTCODE,
    CONF_SCAN_INTERVAL_MINUTES,
    DEFAULT_SCAN_INTERVAL_MINUTES,
    DOMAIN,
    MAX_SCAN_INTERVAL_MINUTES,
    MIN_SCAN_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)


def _scan_interval_selector(default: int) -> vol.Schema:
    """Return a config schema for the scan interval slider."""
    return vol.Schema(
        {
            vol.Required(CONF_SCAN_INTERVAL_MINUTES, default=default): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL_MINUTES,
                    max=MAX_SCAN_INTERVAL_MINUTES,
                    step=5,
                    mode=NumberSelectorMode.SLIDER,
                    unit_of_measurement="min",
                )
            )
        }
    )


def _config_schema() -> vol.Schema:
    """Return the user step schema."""
    return vol.Schema(
        {
            vol.Required(CONF_POSTCODE): str,
            vol.Required(
                CONF_SCAN_INTERVAL_MINUTES,
                default=DEFAULT_SCAN_INTERVAL_MINUTES,
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL_MINUTES,
                    max=MAX_SCAN_INTERVAL_MINUTES,
                    step=5,
                    mode=NumberSelectorMode.SLIDER,
                    unit_of_measurement="min",
                )
            ),
        }
    )


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
                    data={
                        CONF_POSTCODE: postcode,
                        CONF_SCAN_INTERVAL_MINUTES: user_input[
                            CONF_SCAN_INTERVAL_MINUTES
                        ],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(),
            errors=errors,
        )

    async def _async_validate_postcode(self, postcode: str) -> None:
        """Validate that the API accepts the configured postcode."""
        session = async_get_clientsession(self.hass)
        client = NationalGridPowerCutClient(session, postcode)
        await client.async_get_power_cuts()

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return NationalGridPowerCutOptionsFlow(config_entry)


class NationalGridPowerCutOptionsFlow(config_entries.OptionsFlow):
    """Handle options for National Grid Power Cut."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval_minutes = self._config_entry.options.get(
            CONF_SCAN_INTERVAL_MINUTES,
            self._config_entry.data.get(
                CONF_SCAN_INTERVAL_MINUTES,
                DEFAULT_SCAN_INTERVAL_MINUTES,
            ),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=_scan_interval_selector(scan_interval_minutes),
        )
