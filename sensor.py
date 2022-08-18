"""Support for Ecowitt Weather Stations."""
from typing import Final

from aioecowitt import EcoWittListener, EcoWittSensor, EcoWittSensorTypes

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    DEGREE,
    ELECTRIC_POTENTIAL_VOLT,
    LENGTH_MILLIMETERS,
    LENGTH_INCHES,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    LIGHT_LUX,
    PERCENTAGE,
    POWER_WATT,
    PRESSURE_HPA,
    PRESSURE_INHG,
    SPEED_KILOMETERS_PER_HOUR,
    SPEED_MILES_PER_HOUR,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    UV_INDEX,
    AREA_SQUARE_METERS,
)

from .entity import EcowittEntity
from .const import DOMAIN


_METRIC: Final = "metric"
_IMPERIAL: Final = "imperial"


ECOWITT_SENSORS_MAPPING = {
    EcoWittSensorTypes.HUMIDITY: (
        SensorDeviceClass.HUMIDITY,
        PERCENTAGE,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.DEGREE: (None, DEGREE, None, None),
    EcoWittSensorTypes.WATT_METERS_SQUARED: (
        None,
        f"{POWER_WATT}/{AREA_SQUARE_METERS}",
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.UV_INDEX: (None, UV_INDEX, SensorStateClass.MEASUREMENT, None),
    EcoWittSensorTypes.PM25: (
        SensorDeviceClass.PM25,
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.PM10: (
        SensorDeviceClass.PM10,
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.BATTERY_PERCENTAGE: (
        SensorDeviceClass.BATTERY,
        PERCENTAGE,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.BATTERY_VOLTAGE: (
        SensorDeviceClass.VOLTAGE,
        ELECTRIC_POTENTIAL_VOLT,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.CO2_PPM: (
        SensorDeviceClass.CO2,
        CONCENTRATION_PARTS_PER_MILLION,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.LUX: (
        SensorDeviceClass.ILLUMINANCE,
        LIGHT_LUX,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.TIMESTAMP: (SensorDeviceClass.TIMESTAMP, None, None),
    EcoWittSensorTypes.VOLTAGE: (
        SensorDeviceClass.VOLTAGE,
        ELECTRIC_POTENTIAL_VOLT,
        SensorStateClass.MEASUREMENT,
        None,
    ),
    EcoWittSensorTypes.LIGHTNING_COUNT: (
        None,
        "strikes",
        SensorStateClass.TOTAL_INCREASING,
        None,
    ),
    EcoWittSensorTypes.TEMPERATURE_C: (
        SensorDeviceClass.TEMPERATURE,
        TEMP_CELSIUS,
        SensorStateClass.MEASUREMENT,
        _METRIC,
    ),
    EcoWittSensorTypes.TEMPERATURE_F: (
        SensorDeviceClass.TEMPERATURE,
        TEMP_FAHRENHEIT,
        SensorStateClass.MEASUREMENT,
        _IMPERIAL,
    ),
    EcoWittSensorTypes.RAIN_RATE_MM: (
        None,
        LENGTH_MILLIMETERS,
        SensorStateClass.TOTAL_INCREASING,
        _METRIC,
    ),
    EcoWittSensorTypes.RAIN_RATE_INCHES: (
        None,
        LENGTH_INCHES,
        SensorStateClass.TOTAL_INCREASING,
        _IMPERIAL,
    ),
    EcoWittSensorTypes.LIGHTNING_DISTANCE_KM: (
        None,
        LENGTH_KILOMETERS,
        SensorStateClass.MEASUREMENT,
        _METRIC,
    ),
    EcoWittSensorTypes.LIGHTNING_DISTANCE_MILES: (
        None,
        LENGTH_MILES,
        SensorStateClass.MEASUREMENT,
        _IMPERIAL,
    ),
    EcoWittSensorTypes.SPEED_KPH: (
        None,
        SPEED_KILOMETERS_PER_HOUR,
        SensorStateClass.MEASUREMENT,
        _METRIC,
    ),
    EcoWittSensorTypes.SPEED_MPH: (
        None,
        SPEED_MILES_PER_HOUR,
        SensorStateClass.MEASUREMENT,
        _IMPERIAL,
    ),
    EcoWittSensorTypes.PRESSURE_HPA: (
        SensorDeviceClass.PRESSURE,
        PRESSURE_HPA,
        SensorStateClass.MEASUREMENT,
        _METRIC,
    ),
    EcoWittSensorTypes.PRESSURE_INHG: (
        SensorDeviceClass.PRESSURE,
        PRESSURE_INHG,
        SensorStateClass.MEASUREMENT,
        _IMPERIAL,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Add sensors if new."""
    ecowitt: EcoWittListener = hass.data[DOMAIN][entry.entry_id]

    def _new_sensor(sensor: EcoWittSensor) -> None:
        """Add new sensor."""
        if sensor.stype not in ECOWITT_SENSORS_MAPPING:
            return
        mapping = ECOWITT_SENSORS_MAPPING[sensor.stype]

        # Ignore metrics that are not supported by the user's locale
        if mapping[3] == _METRIC and not hass.config.units.is_metric:
            return
        if mapping[3] == _IMPERIAL and hass.config.units.is_metric:
            return

        # Setup sensor description
        description = SensorEntityDescription(
            key=sensor.key,
            name=sensor.name,
            device_class=mapping[0],
            native_unit_of_measurement=mapping[1],
            state_class=mapping[2],
        )

        async_add_entities([EcowittSensorEntity(sensor, description)])

    ecowitt.new_sensor_cb.append(_new_sensor)

    # Add all sensors that are already known
    for sensor in ecowitt.sensors.values():
        _new_sensor(sensor)


class EcowittSensorEntity(EcowittEntity, SensorEntity):
    """Representation of a Ecowitt Sensor."""

    def __init__(
        self, sensor: EcoWittSensor, description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        super().__init__(sensor)
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.ecowitt.value
