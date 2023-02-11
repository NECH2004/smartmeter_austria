"""Test the coordinator."""
from unittest.mock import patch

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import pytest
from smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from smartmeter_austria_energy.obisdata import ObisData, ObisValueString
from smartmeter_austria_energy.smartmeter import Smartmeter
from smartmeter_austria_energy.supplier import SUPPLIER_EVN_NAME

from custom_components.smartmeter_austria.coordinator import SmartmeterDataCoordinator

_COM_PORT = "/dev/ttyUSB1"
_SERIAL_NUMBER = "DEVICE_NUMBER"
_SUPPLIER_NAME = SUPPLIER_EVN_NAME
_HEX_KEY = "my_hex_key"


def test_smartmeter_datacoordinator_constructor(hass):
    """Simple test for construction and initialization."""

    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)

    assert isinstance(coordinator, SmartmeterDataCoordinator)
    assert isinstance(coordinator, DataUpdateCoordinator)


@pytest.mark.asyncio
async def test_smartmeter_datacoordinator_async_update_data(hass):
    """Tests the async_update_data method."""

    with patch.object(Smartmeter, "async_read") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
        with patch.object(ObisData, "DeviceNumber") as device_number_mock:
            device_number_object = ObisValueString(_SERIAL_NUMBER)
            device_number_mock.return_value = device_number_object

            smartmeter_mock.return_value = device_number_mock

            await coordinator._async_update_data()

    assert coordinator.last_update_success


@pytest.mark.asyncio
async def test_smartmeter_datacoordinator_async_update_data_smartmeter_timeout_exception(
    hass,
):
    """Tests the async_update_data method raising a SmartmeterTimeoutException."""

    with pytest.raises(UpdateFailed):
        with patch(
            "smartmeter_austria_energy.smartmeter.Smartmeter"
        ) as smartmeter_mock:
            coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.read"
            ) as read_mock:
                read_mock.side_effect = SmartmeterTimeoutException()

                await coordinator._async_update_data()

    assert coordinator.last_update_success is False


@pytest.mark.asyncio
async def test_smartmeter_datacoordinator_async_update_data_smartmeter_serial_exception(
    hass,
):
    """Tests the async_update_data method raising a SmartmeterSerialException."""

    with pytest.raises(UpdateFailed):
        with patch(
            "smartmeter_austria_energy.smartmeter.Smartmeter"
        ) as smartmeter_mock:
            coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.read"
            ) as read_mock:
                read_mock.side_effect = SmartmeterSerialException()

                await coordinator._async_update_data()

    assert coordinator.last_update_success is False


@pytest.mark.asyncio
async def test_smartmeter_datacoordinator_async_update_data_smartmeter_exception(
    hass,
):
    """Tests the async_update_data method raising a SmartmeterException."""

    with pytest.raises(UpdateFailed):
        with patch(
            "smartmeter_austria_energy.smartmeter.Smartmeter"
        ) as smartmeter_mock:
            coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.read"
            ) as read_mock:
                read_mock.side_effect = SmartmeterException()

                await coordinator._async_update_data()

    assert coordinator.last_update_success is False


@pytest.mark.asyncio
async def test_smartmeter_datacoordinator_async_update_data_exception(
    hass,
):
    """Tests the async_update_data method raising an exception."""

    with pytest.raises(UpdateFailed):
        with patch(
            "smartmeter_austria_energy.smartmeter.Smartmeter"
        ) as smartmeter_mock:
            coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)
            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.read"
            ) as read_mock:
                read_mock.side_effect = Exception()

                await coordinator._async_update_data()

    assert coordinator.last_update_success is False
