"""Test the component setup."""
from unittest.mock import patch
import pytest

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    mock_integration,
)

from homeassistant.exceptions import ConfigEntryNotReady

from serial.tools import list_ports_common


from smartmeter_austria_energy.exceptions import (
    SmartmeterSerialException,
)
from smartmeter_austria_energy.supplier import SUPPLIER_EVN_NAME

from custom_components.smartmeter_austria.__init__ import (
    async_options_update_listener,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)

from custom_components.smartmeter_austria.const import (
    CONF_SUPPLIER_NAME,
    CONF_COM_PORT,
    CONF_KEY_HEX,
    DOMAIN,
    ENTRY_COORDINATOR,
)

from custom_components.smartmeter_austria.coordinator import SmartmeterDataCoordinator

_COM_PORT = "/dev/ttyUSB1"
_SERIAL_NUMBER = "DEVICE_NUMBER"
_SUPPLIER_NAME = SUPPLIER_EVN_NAME
_HEX_KEY = "my_hex_key"


@pytest.mark.asyncio
async def test_async_setup_entry_config_not_ready(hass):
    """Test the integration setup with no connection to the smart meter throwing a ConfigEntryNotReady exception."""

    _data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

    with pytest.raises(ConfigEntryNotReady):
        mock_integration(hass, MockModule(DOMAIN))

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id="my_unique_test_id",
            data=_data,
        )

        config_entry.add_to_hass(hass)

        with patch("smartmeter_austria_energy.smartmeter.Smartmeter.read") as read_mock:
            read_mock.side_effect = SmartmeterSerialException()

            await async_setup_entry(hass, config_entry)


@pytest.mark.asyncio
async def test_async_setup_entry_domain_not_loaded(hass):
    """Test the integration setup and install the domain."""

    _data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data=_data,
    )

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
        assert result


@pytest.mark.asyncio
async def test_async_setup_entry_domain_loaded(hass):
    """Test the integration setup and install the domain."""

    _data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

    hass.data.setdefault(DOMAIN, {})
    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data=_data,
    )

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
        assert result


@pytest.mark.asyncio
async def test_async_unload_entry(hass):
    """Test to unlod the integration."""

    _data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data=_data,
    )

    config_entry.add_to_hass(hass)

    with patch("smartmeter_austria_energy.smartmeter.Smartmeter") as smartmeter_mock:
        coordinator = SmartmeterDataCoordinator(hass, adapter=smartmeter_mock)

        hass.data.setdefault(
            DOMAIN, {config_entry.entry_id: {ENTRY_COORDINATOR: coordinator}}
        )

        test_result = await async_unload_entry(hass, config_entry)
    assert test_result is True


@pytest.mark.asyncio
async def test_async_reload_entry(hass):
    """Test to relod the config entry."""

    _data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data=_data,
    )

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

                        await async_setup_entry(hass, config_entry)

                        # act
                        await async_reload_entry(hass, config_entry)

        result_coordinator = hass.data[DOMAIN].pop(config_entry.entry_id)[
            ENTRY_COORDINATOR
        ]

        assert isinstance(result_coordinator, SmartmeterDataCoordinator)


@pytest.mark.asyncio
async def test_async_options_update_listener(hass):
    """Test the options update listener."""

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

    config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload"
    ) as method_mock:
        # act
        await async_options_update_listener(hass, config_entry)

        # assert
        method_mock.assert_called_once()
