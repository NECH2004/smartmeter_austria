"""Test the coordinator."""
from unittest.mock import patch
import pytest

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
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

    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)

        with patch("smartmeter_austria_energy.smartmeter.Smartmeter.read"):
            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.obisData"
            ) as obisdata_mock:
                obisdata_mock.return_value = "test1"

                obisdata = await coordinator._async_update_data()

                assert obisdata.return_value == "test1"

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
