# ha-nationalgrid-powercut
A Home Assistant custom integration to monitor local National Grid power cut
information by postcode.

The integration queries the National Grid connected data API:

```text
https://connecteddata.nationalgrid.co.uk/api/3/action/datastore_search
```

## Installation

### HACS

[![Open your Home Assistant instance and add this repository to HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=djbenson&repository=ha-nationalgrid-powercut&category=integration)

Use the button above, or add it manually:

1. Open HACS.
2. Go to **Integrations**.
3. Select **Custom repositories** from the menu.
4. Add this repository URL as an **Integration**:

   ```text
   https://github.com/djbenson/ha-nationalgrid-powercut
   ```

5. Install **National Grid Power Cut** and restart Home Assistant.

### Manual

Copy `custom_components/national_grid_power_cut` into your Home Assistant
`custom_components` directory and restart Home Assistant.

## Configuration

[![Open your Home Assistant instance and start setting up a new integration instance.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=national_grid_power_cut)

After installing and restarting Home Assistant, use the button above, or add the
integration from **Settings > Devices & services > Add integration** and search
for **National Grid Power Cut**.

The config flow asks for:

- `Postcode`: the UK postcode to search for live outage records.

## Entities

The integration creates these entities for each configured postcode:

- `binary_sensor.power_cut_reported`: on when the API returns one or more
  matching outage records. Detailed incident records are exposed as attributes.
- `sensor.incident_count`: number of matching outage records.
- `sensor.status`: status for the most relevant/current incident, or
  `No power cut reported`.
- `sensor.estimated_restoration_time`: timestamp from the incident `etr` field.
- `sensor.planned_outage_start`: timestamp for a matching planned outage start.

Fields such as `fault_id`, `category`, `planned`, `resource_status`,
customer counts, voltage, location, reported/restoration dates, and planned
outage details are exposed as attributes on the relevant entities rather than as
standalone sensors.
