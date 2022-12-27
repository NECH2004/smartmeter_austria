"""Sensor platform for Smartmeter Austria Energy."""
from homeassistant.components.sensor import (
    # STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    UpdateFailed,
)
from smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterTimeoutException,
)
from smartmeter_austria_energy.obisdata import ObisData, ObisValue

from .const import DOMAIN, ENTRY_COORDINATOR, ENTRY_DEVICE_INFO, ENTRY_DEVICE_NUMBER
from .coordinator import SmartmeterDataCoordinator
from .sensor_descriptions import _DEFAULT_SENSOR, _SENSOR_DESCRIPTIONS

PARALLEL_UPDATES = 1


# see: https://developers.home-assistant.io/docs/integration_fetching_data/
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator: SmartmeterDataCoordinator = hass.data[DOMAIN][entry.entry_id][
        ENTRY_COORDINATOR
    ]

    async def async_update_data() -> ObisData:
        """Fetch data from the M-BUS device."""
        try:
            coordinator.adapter.read()
            return coordinator.adapter.obisData
        except SmartmeterTimeoutException as err:
            raise UpdateFailed(f"Timeout communicating with API: {err}") from err
        except SmartmeterException as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    coordinator.update_method = async_update_data

    await coordinator.async_config_entry_first_refresh()

    voltagel1_sensor = Sensor("VoltageL1")
    voltagel2_sensor = Sensor("VoltageL2")
    voltagel3_sensor = Sensor("VoltageL3")
    currentl1_sensor = Sensor("CurrentL1")
    currentl2_sensor = Sensor("CurrentL2")
    currentl3_sensor = Sensor("CurrentL3")
    rpi_sensor = Sensor("RealPowerIn")
    rpo_sensor = Sensor("RealPowerOut")
    rei_sensor = Sensor("RealEnergyIn")
    reo_sensor = Sensor("RealEnergyOut")
    reai_sensor = Sensor("ReactiveEnergyIn")
    reao_sensor = Sensor("ReactiveEnergyOut")

    all_sensors = (
        voltagel1_sensor,
        voltagel2_sensor,
        voltagel3_sensor,
        currentl1_sensor,
        currentl2_sensor,
        currentl3_sensor,
        rpi_sensor,
        rpo_sensor,
        rei_sensor,
        reo_sensor,
        reai_sensor,
        reao_sensor,
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
        obisdata: ObisData = self.my_coordinator.adapter.obisData
        if obisdata is None:
            raise ConfigEntryNotReady

        obis_value: ObisValue = getattr(obisdata, self._sensor.sensor_id)
        self._previous_value = obis_value.Value
        return obis_value.Value

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return self.entity_description.entity_category != EntityCategory.DIAGNOSTIC
