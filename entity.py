"""The Ecowitt Weather Station Entity."""
from __future__ import annotations

import time

from aioecowitt import EcoWittSensor

from homeassistant.helpers.entity import Entity, DeviceInfo

from .const import DOMAIN


class EcowittEntity(Entity):
    """Base class for Ecowitt Weather Station."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, sensor: EcoWittSensor) -> None:
        """Construct the entity."""
        self.ecowitt: EcoWittSensor = sensor

        self._attr_name = sensor.name
        self._attr_unique_id = f"{sensor.station.key}-{sensor.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, sensor.station.key),
            },
            name=sensor.station.station,
            model=sensor.station.model,
            sw_version=sensor.station.version,
        )

    async def async_added_to_hass(self):
        """Setup a listener for the entity."""

        def _update_state():
            """Update the state on callback."""
            self.async_schedule_update_ha_state()

        self.ecowitt.update_cb.append(_update_state)

    @property
    def available(self) -> bool:
        """Return whether the state is based on actual reading from device."""
        if (self.ecowitt.last_update_m + 5 * 60) > time.monotonic():
            return True
        return False
