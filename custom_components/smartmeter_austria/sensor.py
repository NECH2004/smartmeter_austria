"""Sensor platform for Smartmeter Austria Energy."""
import async_timeout
from homeassistant.components.sensor import (
    # STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    # UnitOfElectricPotential,
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

from .const import (
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_DEVICE_INFO,
)
from .coordinator import SmartmeterDataCoordinator

# not needed
# SCAN_INTERVAL = timedelta(seconds=30)

PARALLEL_UPDATES = 1


_SENSOR_DESCRIPTIONS = {
    "Voltagel1": SensorEntityDescription(
        key="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,  # UnitOfElectricPotential.VOLT,
        name="Voltage L1",
        icon="mdi:alpha-v-box-outline",
        entity_category=None,
        has_entity_name=True,
    ),
    "Voltagel2": SensorEntityDescription(
        key="V",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,  # UnitOfElectricPotential.VOLT,
        name="Voltage L2",
        icon="mdi:alpha-v-box-outline",
        entity_category=None,
        has_entity_name=True,
    ),
    #    "Voltagel2": SensorEntityDescription(
    #        key="kWh",
    #        device_class=SensorDeviceClass.ENERGY,
    #        state_class=SensorStateClass.TOTAL_INCREASING,
    #        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR
    #        name="Total energy today",
    #        icon="mdi:solar-power",
    #        entity_category=None,
    #        has_entity_name=True,
    #   )
    #    ArrayPosition.communication_status.name: SensorEntityDescription(
    #        key="cloud_status",
    #        name="Cloud connection state",
    #        icon="mdi:cloud-upload",
    #        entity_category=EntityCategory.DIAGNOSTIC,
    #        has_entity_name=True,
    #    ),
    #    ArrayPosition.status.name: SensorEntityDescription(
    #        key="inverter_status",
    #        name="Inverter state",
    #        icon="mdi:solar-power",
    #        entity_category=EntityCategory.DIAGNOSTIC,
    #        has_entity_name=True,
    #    ),
}


_DEFAULT_SENSOR = SensorEntityDescription(
    key="_",
    state_class=STATE_CLASS_MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)


# see: https://developers.home-assistant.io/docs/integration_fetching_data/
async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator: SmartmeterDataCoordinator = hass.data[DOMAIN][entry.entry_id][
        ENTRY_COORDINATOR
    ]

    async def async_update_data() -> ObisData:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
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

    # supplier_name = entry.data[CONF_SUPPLIER_NAME]
    # supplier: Supplier = SUPPLIERS.get(supplier_name)

    voltagel1_sensor = Sensor("VoltageL1")
    voltagel2_sensor = Sensor("VoltageL2")

    all_sensors = (voltagel1_sensor, voltagel2_sensor)

    device_info: DeviceInfo = hass.data[DOMAIN][entry.entry_id][ENTRY_DEVICE_INFO]
    serial_number = ""

    entities = []

    # Individual inverter sensors entities
    entities.extend(
        SmartmeterSensor(coordinator, device_info, serial_number, sensor)
        for sensor in all_sensors
    )

    async_add_entities(entities)


class Sensor:
    """Defines a sensor of the Smartmeter"""

    def __init__(self, sensor_id: str) -> None:
        self._sensor_id = sensor_id

    @property
    def sensor_id(self) -> str:
        """The Smartmeter sensor ID."""
        return self._sensor_id


class SmartmeterSensor(CoordinatorEntity, SensorEntity):
    """Entity representing an smartmeter sensor."""

    def __init__(
        self,
        coordinator: SmartmeterDataCoordinator,
        device_info: DeviceInfo,
        serial_number: str,
        sensor: Sensor,
    ) -> None:
        """Initialize an inverter sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{DOMAIN}_{serial_number}_{sensor.sensor_id}"
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
