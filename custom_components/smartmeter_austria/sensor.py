"""Sensor platform for Smartmeter Austria Energy."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from smartmeter_austria_energy.exceptions import SmartmeterException
from smartmeter_austria_energy.obisdata import ObisData, ObisValueFloat, ObisValueBytes

from .const import DOMAIN
from .coordinator import SmartmeterDataCoordinator
from .sensor_descriptions import DEFAULT_SENSOR, SENSOR_DESCRIPTIONS
from .smartmeter_config_entry import SmartMeterConfigEntry

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1


# hass: HomeAssistant,
#    entry: MyConfigEntry,  # use type alias instead of ConfigEntry
#    async_add_entities: AddEntitiesCallback
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Do a setup of the sensor platform."""

    my_config: SmartMeterConfigEntry = entry.runtime_data
    coordinator: SmartmeterDataCoordinator = my_config.coordinator

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

    device_info: DeviceInfo = my_config.device_info
    device_number: str = my_config.device_number

    entities = []

    # Individual inverter sensors entities
    for sensor in all_sensors:
        if any(sensor.sensor_id in x for x in coordinator.adapter.supplier.supplied_values):
            mySensor = SmartmeterSensor(
                coordinator, device_info, device_number, sensor)
            entities.append(mySensor)

    async_add_entities(entities)


class Sensor:
    """Defines a sensor of the smartmeter."""

    def __init__(self, sensor_id: str) -> None:
        """Initialize."""
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
        self.entity_description = SENSOR_DESCRIPTIONS.get(
            sensor.sensor_id, DEFAULT_SENSOR
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
            obis_value: ObisValueFloat | ObisValueBytes = getattr(
                obisdata, self._sensor.sensor_id
            )
            if obis_value is None:
                _LOGGER.debug("obisdata is None.")
                raise ConfigEntryNotReady()

            new_value = obis_value.value
            self._previous_value = new_value
            return new_value
        except SmartmeterException as exception:
            _LOGGER.debug("native_value has an error. %s",
                          exception, exc_info=True)
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
