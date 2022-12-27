"""Test the config flow."""
from unittest.mock import patch
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
)

from homeassistant.config_entries import OptionsFlow

from serial.tools import list_ports_common

from smartmeter_austria_energy.supplier import SUPPLIER_EVN_NAME

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
    OPT_DATA_INTERVAL,
)

_COM_PORT = "/dev/ttyUSB1"
_SERIAL_NUMBER = "DEVICE_NUMBER"
_SUPPLIER_NAME = SUPPLIER_EVN_NAME
_HEX_KEY = "my_hex_key"


def test_smartmeter_config_flow_constructor():
    """Simple test for construction and initialization."""
    result_flow_handler = SmartmeterConfigFlow()

    assert isinstance(result_flow_handler, SmartmeterConfigFlow)


@pytest.mark.asyncio
async def test_smartmeter_config_flow_async_step_user_user_input_is_none(hass):
    """Tests the user step without valid user data."""
    result_flow_handler = SmartmeterConfigFlow()
    result_flow_handler.hass = hass

    my_flow_result = await result_flow_handler.async_step_user()

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "user"
    assert my_flow_result["errors"] == {}


@pytest.mark.asyncio
async def test_smartmeter_config_flow_async_step_user_user_input_id_loaded_new_smartmeter(
    hass,
):
    """Tests the user step with user data and inverter is not configured yet."""
    result_flow_handler = SmartmeterConfigFlow()
    result_flow_handler.hass = hass

    data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }

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

                        with patch(
                            "custom_components.smartmeter_austria.config_flow.SmartmeterConfigFlow.async_set_unique_id"
                        ):

                            my_flow_result = await result_flow_handler.async_step_user(
                                user_input=data
                            )

    assert my_flow_result["type"] == "create_entry"


@pytest.mark.asyncio
async def test_smartmeter_config_flow_async_step_user_user_input_id_other_smartmeter(
    hass,
):
    """Tests the user step with user data and other configured smart meter."""
    result_flow_handler = SmartmeterConfigFlow()
    result_flow_handler.hass = hass

    com_port2 = "/dev/ttyUSB3"

    data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
        CONF_SERIAL_NO: _SERIAL_NUMBER,
    }

    mock_config = MockConfigEntry(domain=DOMAIN, data=data)
    with patch("serial.tools.list_ports.comports") as comports_mock:
        com_port_info = list_ports_common.ListPortInfo(com_port2, True)
        comports_result: list[list_ports_common.ListPortInfo] = [com_port_info]
        comports_mock.return_value = comports_result

        with patch(
            "custom_components.smartmeter_austria.config_flow.SmartmeterConfigFlow._async_current_entries"
        ) as current_entries_mock:
            current_entries_mock.return_value = {mock_config}

            with patch(
                "smartmeter_austria_energy.smartmeter.Smartmeter.read"
            ) as smartmeter_read_mock:
                smartmeter_read_mock.return_value = "test1"

                with patch("smartmeter_austria_energy.smartmeter.Smartmeter.obisData"):
                    with patch(
                        "smartmeter_austria_energy.smartmeter.Smartmeter.obisData.DeviceNumber.RawValue.decode"
                    ) as obisdata_device_number_mock:
                        obisdata_device_number_mock.return_value = _SERIAL_NUMBER

                        with patch(
                            "custom_components.smartmeter_austria.config_flow.SmartmeterConfigFlow.async_set_unique_id"
                        ):
                            my_flow_result = await result_flow_handler.async_step_user(
                                user_input=data
                            )

    assert my_flow_result["type"] == "create_entry"


@pytest.mark.asyncio
async def test_smartmeter_config_flow_async_get_options_flow():
    """Tests the async_get_options_flow."""

    flow_handler = SmartmeterConfigFlow()
    options_flow = OptionsFlow()

    result = flow_handler.async_get_options_flow(options_flow)

    assert isinstance(result, SmartMeterOptionsFlowHandler)


@pytest.mark.asyncio
async def test_smart_meter_options_flow_handler_constructor():
    """Simple test for construction and initialization."""

    data = {
        CONF_SUPPLIER_NAME: _SUPPLIER_NAME,
        CONF_COM_PORT: _COM_PORT,
        CONF_KEY_HEX: _HEX_KEY,
    }
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = SmartMeterOptionsFlowHandler(config_entry)

    assert isinstance(options_flow_handler, SmartMeterOptionsFlowHandler)


@pytest.mark.asyncio
async def test_smart_meter_options_flow_handler_async_step_init_no_user_input():
    """Tests the init step without user input."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=None)

    options_flow_handler = SmartMeterOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=None)

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "init"
    assert my_flow_result["errors"] == {}


@pytest.mark.asyncio
async def test_smart_meter_options_flow_handler_async_step_init_user_input():
    """Tests the init step with valid user input."""
    data = {OPT_DATA_INTERVAL: 10}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = SmartMeterOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=data)

    assert my_flow_result["type"] == "create_entry"


@pytest.mark.asyncio
async def test_smart_meter_options_flow_handler_async_step_init_interval_empty():
    """Tests the init step with empty interval data."""
    data = {OPT_DATA_INTERVAL: None}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = SmartMeterOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=data)

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "init"
    assert my_flow_result["errors"] == {"base": "data_interval_empty"}


@pytest.mark.asyncio
async def test_smart_meter_options_flow_handler_async_step_init_interval_wrong():
    """Tests the init step with invalid interval data."""
    data = {OPT_DATA_INTERVAL: 1}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = SmartMeterOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=data)

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "init"
    assert my_flow_result["errors"] == {"base": "data_interval_wrong"}
