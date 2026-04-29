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
- `Refresh interval`: how often to poll the National Grid API, from 5 to 60
  minutes.

The refresh interval can be changed later from the integration's options.

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

## Automation example

The automation will fire either when there is a live power cut or a planned power cut is detected.

```
alias: National Grid Power Cut Alerts
description: Notify when a live or planned National Grid power cut is detected.
mode: single

trigger:
  - platform: state
    entity_id: binary_sensor.power_cut_reported
    from: "off"
    to: "on"
    id: live_power_cut

  - platform: time
    at: sensor.planned_outage_start
    id: planned_power_cut

condition: []

action:
  - choose:
      - conditions:
          - condition: trigger
            id: live_power_cut
        sequence:
          - service: notify.mobile_app_your_phone
            data:
              title: Power cut reported
              message: >
                National Grid has reported a power cut for your postcode.
                Status: {{ states('sensor.status') }}.
                Estimated restoration:
                {% if states('sensor.estimated_restoration_time') not in ['unknown', 'unavailable', 'none'] %}
                  {{ as_timestamp(states('sensor.estimated_restoration_time')) | timestamp_custom('%H:%M on %d %b') }}
                {% else %}
                  Not currently available.
                {% endif %}

      - conditions:
          - condition: trigger
            id: planned_power_cut
        sequence:
          - service: notify.mobile_app_your_phone
            data:
              title: Planned power cut
              message: >
                A planned power cut is scheduled to start now.
                Status: {{ states('sensor.status') }}.
                Estimated restoration:
                {% if states('sensor.estimated_restoration_time') not in ['unknown', 'unavailable', 'none'] %}
                  {{ as_timestamp(states('sensor.estimated_restoration_time')) | timestamp_custom('%H:%M on %d %b') }}
                {% else %}
                  Not currently available.
                {% endif %}
```
