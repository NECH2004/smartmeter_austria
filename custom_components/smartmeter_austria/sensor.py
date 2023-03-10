"""Sensor platform for Smartmeter Austria Energy."""
import logging

from homeassistant.components.sensor import (  # STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from smartmeter_austria_energy.exceptions import SmartmeterException
from smartmeter_austria_energy.obisdata import ObisData, ObisValueFloat, ObisValueString

from .const import DOMAIN, ENTRY_COORDINATOR, ENTRY_DEVICE_INFO, ENTRY_DEVICE_NUMBER
from .coordinator import SmartmeterDataCoordinator
from .sensor_descriptions import _DEFAULT_SENSOR, _SENSOR_DESCRIPTIONS

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


# see: https://developers.home-assistant.io/docs/integration_fetching_data/
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator: SmartmeterDataCoordinator = hass.data[DOMAIN][entry.entry_id][
        ENTRY_COORDINATOR
    ]

    all_sensors = (
        Sensor("VoltageL1"),
        Sensor("VoltageL2"),
        Sensor("VoltageL3"),
        Sensor("CurrentL1"),
        Sensor("CurrentL2"),
        Sensor("CurrentL3"),
        Sensor("RealPowerIn"),
        Sensor("RealPowerOut"),
        Sensor("RealPowerDelta"),
        Sensor("RealEnergyIn"),
        Sensor("RealEnergyOut"),
        Sensor("ReactiveEnergyIn"),
        Sensor("ReactiveEnergyOut"),
    )

    device_info: DeviceInfo = hass.data[DOMAIN][entry.entry_id][ENTRY_DEVICE_INFO]
    device_number = hass.data[DOMAIN][entry.entry_id][ENTRY_DEVICE_NUMBER]

    entities = []

    # Individual inverter sensors entities
    entities.extend(
        SmartmeterSensor(coordinator, device_info, device_number, sensor)
        for sensor in all_sensors
    )

    async_add_entities(entities)


class Sensor:
    """Defines a sensor of the smartmeter"""

    def __init__(self, sensor_id: str) -> None:
        self._sensor_id = sensor_id

    @property
    def sensor_id(self) -> str:
        """The Smartmeter sensor ID."""
        return self._sensor_id


class SmartmeterSensor(CoordinatorEntity, SensorEntity):
    """Entity representing a smartmeter sensor."""

    def __init__(
        self,
        coordinator: SmartmeterDataCoordinator,
        device_info: DeviceInfo,
        device_number: str,
        sensor: Sensor,
    ) -> None:
        """Initialize a sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{DOMAIN}_{device_number}_{sensor.sensor_id}"
        self._attr_device_info = device_info
        self.entity_description = _SENSOR_DESCRIPTIONS.get(
            sensor.sensor_id, _DEFAULT_SENSOR
        )
        self._sensor = sensor
        self._previous_value = None
        self.my_coordinator = coordinator

    @property
    def native_value(self):
        """Return the value reported by the sensor."""
        obisdata: ObisData = self.my_coordinator.data
        if obisdata is None:
            raise ConfigEntryNotReady

        try:
            obis_value: ObisValueFloat | ObisValueString = getattr(
                obisdata, self._sensor.sensor_id
            )
            if obis_value is None:
                _LOGGER.debug("obisdata is None.")
                raise ConfigEntryNotReady()

            new_value = obis_value.Value
            self._previous_value = new_value
            return new_value
        except SmartmeterException as exception:
            _LOGGER.debug("native_value has an error. %s", exception, exc_info=True)
            raise ConfigEntryNotReady() from exception
        except Exception as exception:
            _LOGGER.warning(
                "native_value has a generic error. %s", exception, exc_info=True
            )
            raise ConfigEntryNotReady() from exception

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self.entity_description.entity_category != EntityCategory.DIAGNOSTIC
