"""Description of all sensors."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.helpers.entity import EntityCategory

SENSOR_DESCRIPTIONS = {
    "VoltageL1": SensorEntityDescription(
        key="voltagel1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        name="Voltage L1",
        icon="mdi:flash-triangle-outline",
        entity_category=None,
        has_entity_name=True,
    ),
    "VoltageL2": SensorEntityDescription(
        key="voltagel2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        name="Voltage L2",
        icon="mdi:flash-triangle-outline",
        entity_category=None,
        has_entity_name=True,
    ),
    "VoltageL3": SensorEntityDescription(
        key="voltagel3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        name="Voltage L3",
        icon="mdi:flash-triangle-outline",
        entity_category=None,
        has_entity_name=True,
    ),
    "CurrentL1": SensorEntityDescription(
        key="currentl1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        name="Current L1",
        icon="mdi:current-ac",
        entity_category=None,
        has_entity_name=True,
    ),
    "CurrentL2": SensorEntityDescription(
        key="currentl2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        name="Current L2",
        icon="mdi:current-ac",
        entity_category=None,
        has_entity_name=True,
    ),
    "CurrentL3": SensorEntityDescription(
        key="currentl3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        name="Current L3",
        icon="mdi:current-ac",
        entity_category=None,
        has_entity_name=True,
    ),
    "RealPowerIn": SensorEntityDescription(
        key="realpowerin",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power in",
        icon="mdi:transmission-tower-export",
        entity_category=None,
        has_entity_name=True,
    ),
    "RealPowerOut": SensorEntityDescription(
        key="realpowerout",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power out",
        icon="mdi:transmission-tower-import",
        entity_category=None,
        has_entity_name=True,
    ),
    "RealPowerDelta": SensorEntityDescription(
        key="realpowerdelta",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power delta",
        icon="mdi:transmission-tower",
        entity_category=None,
        has_entity_name=True,
    ),
    "RealEnergyIn": SensorEntityDescription(
        key="realenergyin",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        name="Real energy in",
        icon="mdi:transmission-tower-export",
        entity_category=None,
        has_entity_name=True,
    ),
    "RealEnergyOut": SensorEntityDescription(
        key="realenergyout",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        name="Real energy out",
        icon="mdi:transmission-tower-import",
        entity_category=None,
        has_entity_name=True,
    ),
    "ReactiveEnergyIn": SensorEntityDescription(
        key="reactiveenergyin",
        # device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",  # UnitOfEnergy.WATT_HOUR
        name="Reactive energy in",
        icon="mdi:transmission-tower-export",
        entity_category=None,
        has_entity_name=True,
    ),
    "ReactiveEnergyOut": SensorEntityDescription(
        key="reactiveenergyout",
        # device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",  # UnitOfEnergy.WATT_HOUR
        name="Reactive energy out",
        icon="mdi:transmission-tower-import",
        entity_category=None,
        has_entity_name=True,
    ),
}


DEFAULT_SENSOR = SensorEntityDescription(
    key="_",
    state_class=SensorStateClass.MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)
