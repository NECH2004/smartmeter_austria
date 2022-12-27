"""Tests the smartmeter sensors"""
"""Test the component setup."""
from unittest.mock import patch
import pytest

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    mock_integration,
)

from homeassistant.config_entries import OptionsFlow
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import UpdateFailed

from serial.tools import list_ports_common

from smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from smartmeter_austria_energy.supplier import SUPPLIER_EVN_NAME

from custom_components.smartmeter_austria.__init__ import (
    async_options_update_listener,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.smartmeter_austria.config_flow import (
    SmartmeterConfigFlow,
    SmartMeterOptionsFlowHandler,
)

from custom_components.smartmeter_austria.const import (
    CONF_SUPPLIER_NAME,
    CONF_COM_PORT,
    CONF_KEY_HEX,
    CONF_SERIAL_NO,
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_DEVICE_INFO,
    OPT_DATA_INTERVAL,
)

from custom_components.smartmeter_austria.coordinator import SmartmeterDataCoordinator

_COM_PORT = "/dev/ttyUSB1"
_SERIAL_NUMBER = "DEVICE_NUMBER"
_SUPPLIER_NAME = SUPPLIER_EVN_NAME
_HEX_KEY = "my_hex_key"


def async_add_entities(entities):
    """Add entities to a sensor as simuation for unit test. Helper method."""
    count = entities.__len__()
    assert count == 4


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

    with patch("serial.tools.list_ports.comports") as comports_mock:
        com_port_info = list_ports_common.ListPortInfo(_COM_PORT, True)
        comports_result: list[list_ports_common.ListPortInfo] = [com_port_info]
        comports_mock.return_value = comports_result
        with patch(
            "custom_components.smartmeter_austria.config_flow.SmartmeterConfigFlow._async_current_entries"
        ) as current_entries_mock:
            current_entries_mock.return_value = {}

            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.read"
            ) as smartmeter_read_mock:
                smartmeter_read_mock.return_value = "test1"

                with patch("smartmeter_austria_energy.smartmeter.Smartmeter.obisData"):
                    with patch(
                        "smartmeter_austria_energy.smartmeter.Smartmeter.obisData.DeviceNumber.RawValue.decode"
                    ) as obisdata_device_number_mock:
                        obisdata_device_number_mock.return_value = _SERIAL_NUMBER

                        result = await async_setup_entry(hass, config_entry)
    assert result is True
