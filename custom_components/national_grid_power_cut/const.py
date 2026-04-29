"""Constants for the National Grid Power Cut integration."""

from __future__ import annotations

DOMAIN = "national_grid_power_cut"

CONF_POSTCODE = "postcode"
CONF_SCAN_INTERVAL_MINUTES = "scan_interval_minutes"

API_URL = "https://connecteddata.nationalgrid.co.uk/api/3/action/datastore_search"
RESOURCE_ID = "a1365982-4e05-463c-8304-8323a2ba0ccd"

DEFAULT_SCAN_INTERVAL_MINUTES = 5
MIN_SCAN_INTERVAL_MINUTES = 5
MAX_SCAN_INTERVAL_MINUTES = 60
