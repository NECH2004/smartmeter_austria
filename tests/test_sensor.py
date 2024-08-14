"""Tests the smartmeter sensors."""
from unittest.mock import patch

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    mock_integration,
)
from serial.tools import list_ports_common
import serial.tools.list_ports
from smartmeter_austria_energy.obisdata import ObisData, ObisValueBytes
from smartmeter_austria_energy.smartmeter import Smartmeter
from smartmeter_austria_energy.supplier import SUPPLIER_EVN_NAME

from custom_components.smartmeter_austria.config_flow import SmartmeterConfigFlow
from custom_components.smartmeter_austria.const import (
    CONF_COM_PORT,
    CONF_KEY_HEX,
    CONF_SUPPLIER_NAME,
    DOMAIN,
)
from custom_components.smartmeter_austria.coordinator import SmartmeterDataCoordinator
from custom_components.smartmeter_austria.sensor import (
    Sensor,
    SmartmeterSensor,
    async_setup_entry,
)
from custom_components.smartmeter_austria.smartmeter_data import SmartMeterData

_COM_PORT = "/dev/ttyUSB1"
_SERIAL_NUMBER = "DEVICE_NUMBER"
_SUPPLIER_NAME = SUPPLIER_EVN_NAME
_HEX_KEY = "my_hex_key"


def async_add_entities(entities):
    """Add entities to a sensor as simuation for unit test. Helper method."""
    count = entities.__len__()
    assert count == 13


@pytest.mark.asyncio
async def test_async_setup_entry(hass):
    """Test the sensor setup."""
    mock_integration(hass, MockModule(DOMAIN))

    _data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data=_data,
    )

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    config_entry.add_to_hass(hass)

    with patch.object(serial.tools.list_ports, "comports") as comports_mock:
        com_port_info = list_ports_common.ListPortInfo(_COM_PORT, True)
        comports_result: list[list_ports_common.ListPortInfo] = [com_port_info]
        comports_mock.return_value = comports_result

        with patch.object(
            SmartmeterConfigFlow, "_async_current_entries"
        ) as current_entries_mock:
            current_entries_mock.return_value = {}
            with patch.object(Smartmeter, "read") as smartmeter_mock:
                coordinator = SmartmeterDataCoordinator(
                    hass, adapter=smartmeter_mock)
                with patch.object(ObisData, "DeviceNumber") as device_number_mock:
                    device_number_object = ObisValueBytes(_SERIAL_NUMBER)
                    device_number_mock.return_value = device_number_object

                    smartmeter_mock.return_value = device_number_mock

                    device_info = DeviceInfo()

                    my_config = SmartMeterData(
                        coordinator=coordinator, device_info=device_info, device_number=_SERIAL_NUMBER)
                    config_entry.runtime_data = my_config

                    await async_setup_entry(hass, config_entry, async_add_entities)
    # assert
    # is done in async_add_entities


def test_sensor_constructor():
    """Simple test for sensor construction and initialization."""
    sensor_id = "sensor_3"
    result_sensor = Sensor(sensor_id)

    assert isinstance(result_sensor, Sensor)


def test_sensor_sensor_id():
    """Simple test for sensor construction and initialization."""
    sensor_id = "sensor_3"
    my_sensor = Sensor(sensor_id)

    result = my_sensor.sensor_id

    assert result == sensor_id


def test_smartsensor_constructor(hass):
    """Simple test for smartsensor construction and initialization."""
    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
        device_info = DeviceInfo()
        device_number = "number 1"
        sensor_id = "sensor_3"
        sensor = Sensor(sensor_id)

        result_sensor = SmartmeterSensor(
            coordinator, device_info, device_number, sensor
        )

    assert isinstance(result_sensor, SmartmeterSensor)
    assert isinstance(result_sensor, CoordinatorEntity)
    assert isinstance(result_sensor, SensorEntity)


def test_smartsensor_entity_registry_enabled_default_false_for_diagnostic_sensor(hass):
    """Simple test for smartsensor construction and initialization."""

    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
        device_info = DeviceInfo()
        device_number = "number 1"
        sensor_id = "sensor_3"
        sensor = Sensor(sensor_id)
        smartsensor = SmartmeterSensor(
            coordinator, device_info, device_number, sensor)

        result = smartsensor.entity_registry_enabled_default

    assert result is False


def test_smartsensor_entity_registry_enabled_default_false_for_known_sensor(hass):
    """Simple test for smartsensor construction and initialization."""
    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
        device_info = DeviceInfo()
        device_number = "number 1"

        voltagel1_sensor = Sensor("VoltageL1")

        smartsensor = SmartmeterSensor(
            coordinator, device_info, device_number, voltagel1_sensor
        )

        result = smartsensor.entity_registry_enabled_default

    assert result is True


def test_smartsensor_entity_registry_native_value_property(hass):
    """Simple test for smartsensor construction and initialization."""
    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
        coordinator.data = ObisData(dec=None, wanted_values=[])

        device_info = DeviceInfo()
        device_number = "number 1"

        sensor = Sensor("VoltageL1")

        smartsensor = SmartmeterSensor(
            coordinator, device_info, device_number, sensor)

        result = smartsensor.native_value

    assert result is not None
