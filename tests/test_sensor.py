"""Sensor tests."""
from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed
import httpx
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from zever_local.inverter import InverterData, ZeversolarError, ZeversolarTimeout

from custom_components.zeversolar_local.const import (
    CONF_SERIAL_NO,
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_DEVICE_INFO,
)
from custom_components.zeversolar_local.coordinator import (
    ZeverSolarApiClient,
    ZeversolarApiCoordinator,
)
from custom_components.zeversolar_local.sensor import (
    Inverter,
    Sensor,
    ZeverSolarSensor,
    async_setup_entry,
)

_registry_id = "EAB241277A36"
_registry_key = "ZYXTBGERTXJLTSVS"
_hardware_version = "M11"
_software_version = "18625-797R+17829-719R"
_time = "16:22"
_date = "20/02/2022"
_serial_number = "ZS150045138C0104"
_content = f"1\n1\n{_registry_id}\n{_registry_key}\n{_hardware_version}\n{_software_version}\n{_time} {_date}\n1\n1\n{_serial_number}\n1234\n8.9\nOK\nError"

_byte_content = _content.encode()


def async_add_entities(entities):
    """Add entities to a sensor as simuation for unit test. Helper method."""
    count = entities.__len__()
    assert count == 4


async def test_async_setup_entry(hass):
    """Tests the setup of the sensor platform."""
    host = "TEST_HOST"
    client = ZeverSolarApiClient(host)
    coordinator = ZeversolarApiCoordinator(hass, client=client)

    serial_number = "ABC"
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: serial_number},
    )

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    config_entry.add_to_hass(hass)

    device_info = DeviceInfo()
    hass.data[DOMAIN][config_entry.entry_id] = {
        ENTRY_COORDINATOR: coordinator,
        ENTRY_DEVICE_INFO: device_info,
    }

    mock_response = httpx.Response(
        200, request=httpx.Request("Get", f"https://{host}"), content=_byte_content
    )

    with patch("zever_local.inverter.httpx.AsyncClient.get") as mock_device_info:
        mock_device_info.return_value = mock_response

        await async_setup_entry(hass, config_entry, async_add_entities)


async def test_async_setup_entry_coordinator_update_ok(hass):
    """Tests the sensor platform with updating data."""
    host = "TEST_HOST"
    client = ZeverSolarApiClient(host)
    coordinator = ZeversolarApiCoordinator(hass, client=client)
    serial_number = "Any_Number"

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: serial_number},
    )

    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    config_entry.add_to_hass(hass)

    device_info = DeviceInfo()
    hass.data[DOMAIN][config_entry.entry_id] = {
        ENTRY_COORDINATOR: coordinator,
        ENTRY_DEVICE_INFO: device_info,
    }

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content
        )
        api_mock.return_value = mock_response

        await async_setup_entry(hass, config_entry, async_add_entities)
        my_solardata: InverterData = await coordinator.update_method()
        assert my_solardata.energy_today_KWh == 8.09


async def test_async_setup_entry_coordinator_update_fails_with_timeout(hass):
    """Tests of the sensor platform with updating data failing."""
    with pytest.raises(UpdateFailed):
        host = "TEST_HOST"
        client = ZeverSolarApiClient(host)
        coordinator = ZeversolarApiCoordinator(hass, client=client)
        serial_number = "test"

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id="my_unique_test_id",
            data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: serial_number},
        )

        if hass.data.get(DOMAIN) is None:
            hass.data.setdefault(DOMAIN, {})

        config_entry.add_to_hass(hass)

        device_info = DeviceInfo()
        hass.data[DOMAIN][config_entry.entry_id] = {
            ENTRY_COORDINATOR: coordinator,
            ENTRY_DEVICE_INFO: device_info,
        }

        with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
            mock_response = httpx.Response(
                200,
                request=httpx.Request("Get", "https://test.t"),
                content=_byte_content,
            )
            api_mock.return_value = mock_response

            await async_setup_entry(hass, config_entry, async_add_entities)

        with patch(
            "zever_local.inverter.httpx.AsyncClient.get"
        ) as api_mock_solardata_fail:
            api_mock_solardata_fail.side_effect = ZeversolarTimeout("Timeout happened")
            await coordinator.update_method()


async def test_async_setup_entry_coordinator_update_fails_with_error(hass):
    """Tests the sensor platform with update failing."""
    with pytest.raises(UpdateFailed):
        host = "TEST_HOST"
        client = ZeverSolarApiClient(host)
        coordinator = ZeversolarApiCoordinator(hass, client=client)
        serial_number = "145e-serxsdtr"

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id="my_unique_test_id",
            data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: serial_number},
        )

        if hass.data.get(DOMAIN) is None:
            hass.data.setdefault(DOMAIN, {})

        config_entry.add_to_hass(hass)

        device_info = DeviceInfo()
        hass.data[DOMAIN][config_entry.entry_id] = {
            ENTRY_COORDINATOR: coordinator,
            ENTRY_DEVICE_INFO: device_info,
        }

        with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
            mock_response = httpx.Response(
                200,
                request=httpx.Request("Get", "https://test.t"),
                content=_byte_content,
            )
            api_mock.return_value = mock_response

            await async_setup_entry(hass, config_entry, async_add_entities)

        with patch(
            "zever_local.inverter.httpx.AsyncClient.get"
        ) as api_mock_solardata_fail:
            api_mock_solardata_fail.side_effect = ZeversolarError("Error happened")
            await coordinator.update_method()


async def test_Sensor_class(hass):
    """Simple test for construction and initialization."""
    sensor_id = "sensor_1"

    result_sensor = Sensor(sensor_id)
    result_sensor_id = result_sensor.sensor_id

    assert type(result_sensor) is Sensor
    assert sensor_id == result_sensor_id


async def test_Inverter_class(hass):
    """Simple test for construction and initialization."""
    serial_number = "ABC_x34"
    address = "10.10.10.1"
    hardware_version = "h v"
    software_version = "sw"

    result_inverter = Inverter(
        serial_number, address, hardware_version, software_version
    )
    result_serial_number = result_inverter.serial_number

    assert type(result_inverter) is Inverter
    assert serial_number == result_serial_number


async def test_ZeverSolarSensor_class(hass):
    """Simple test for construction and initialization."""
    serial_number = "ABC_x34"
    address = "10.10.10.1"
    hardware_version = "h v"
    software_version = "sw"
    inverter = Inverter(serial_number, address, hardware_version, software_version)
    sensor_id = "sensor_1"
    sensor = Sensor(sensor_id)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, inverter.serial_number)},
        name=f"ZeverSolar inverter '{inverter.serial_number}'",
        manufacturer="ZeverSolar",
        hw_version="M10",
        sw_version="17717-709R+17511-707R",
    )

    api_client = ZeverSolarApiClient("TEST_HOST")
    coordinator = ZeversolarApiCoordinator(hass, api_client)
    result_sensor = ZeverSolarSensor(
        coordinator, device_info, inverter.serial_number, sensor
    )

    assert type(result_sensor) is ZeverSolarSensor


async def test_ZeverSolarSensor_native_value_no_data(hass):
    """Fetch data from coordinator but data is None."""
    with pytest.raises(ConfigEntryNotReady):
        serial_number = "ABC_x34"
        address = "10.10.10.1"
        hardware_version = "h v"
        software_version = "sw"
        inverter = Inverter(serial_number, address, hardware_version, software_version)
        sensor_id = "power"
        sensor = Sensor(sensor_id)

        device_info = DeviceInfo(
            identifiers={(DOMAIN, inverter.serial_number)},
            name=f"ZeverSolar inverter '{inverter.serial_number}'",
            manufacturer="ZeverSolar",
            hw_version="M10",
            sw_version="17717-709R+17511-707R",
        )

        api_client = ZeverSolarApiClient("TEST_HOST")
        coordinator = ZeversolarApiCoordinator(hass, api_client)

        zeversolar_sensor = ZeverSolarSensor(
            coordinator, device_info, inverter.serial_number, sensor
        )

        with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
            api_mock.return_value = None
            await coordinator.async_config_entry_first_refresh()
            zeversolar_sensor.native_value


async def test_ZeverSolarSensor_native_value_data(hass):
    """Fetch data from coordinator and data can be fetched."""

    serial_number = "ABC_x34"
    address = "10.10.10.1"
    hardware_version = "h v"
    software_version = "sw"
    inverter = Inverter(serial_number, address, hardware_version, software_version)
    sensor_id = "pac_watt"
    sensor = Sensor(sensor_id)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, inverter.serial_number)},
        name=f"ZeverSolar inverter '{inverter.serial_number}'",
        manufacturer="ZeverSolar",
        hw_version="M10",
        sw_version="17717-709R+17511-707R",
    )

    api_client = ZeverSolarApiClient("TEST_HOST")
    coordinator = ZeversolarApiCoordinator(hass, api_client)

    zeversolar_sensor = ZeverSolarSensor(
        coordinator, device_info, inverter.serial_number, sensor
    )

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content
        )
        api_mock.return_value = mock_response

        await coordinator.async_config_entry_first_refresh()

        result_native_value = zeversolar_sensor.native_value

    assert result_native_value == 1234


async def test_ZeverSolarSensor_native_value_ZeverTimeout_exception(hass):
    """Fetch data from coordinator and data can be fetched."""
    with pytest.raises(ConfigEntryNotReady):
        serial_number = "ABC_x34"
        address = "10.10.10.1"
        hardware_version = "h v"
        software_version = "sw"
        inverter = Inverter(serial_number, address, hardware_version, software_version)
        sensor_id = "power"
        sensor = Sensor(sensor_id)

        device_info = DeviceInfo(
            identifiers={(DOMAIN, inverter.serial_number)},
            name=f"ZeverSolar inverter '{inverter.serial_number}'",
            manufacturer="ZeverSolar",
            hw_version="M10",
            sw_version="17717-709R+17511-707R",
        )

        api_client = ZeverSolarApiClient("TEST_HOST")
        coordinator = ZeversolarApiCoordinator(hass, api_client)

        zeversolar_sensor = ZeverSolarSensor(
            coordinator, device_info, inverter.serial_number, sensor
        )

        with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
            api_mock.side_effect = ZeversolarTimeout("uups")
            await coordinator.async_config_entry_first_refresh()

            zeversolar_sensor.native_value
