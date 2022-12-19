"""Test the config flow."""
from unittest.mock import patch

from homeassistant.config_entries import OptionsFlow
from homeassistant.const import CONF_HOST
import httpx
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.zeversolar_local.config_flow import (
    ZeverSolarFlowHandler,
    ZeverSolarOptionsFlowHandler,
)
from custom_components.zeversolar_local.const import (
    CONF_SERIAL_NO,
    DOMAIN,
    OPT_DATA_INTERVAL,
)

_registry_id = "EAB241277A36"
_registry_key = "ZYXTBGERTXJLTSVS"
_hardware_version = "M11"
_software_version = "18625-797R+17829-719R"
_time = "16:22"
_date = "20/02/2022"
_serial_number = "ZS150045138C0104"
_content = f"1\n1\n{_registry_id}\n{_registry_key}\n{_hardware_version}\n{_software_version}\n{_time} {_date}\n1\n1\n{_serial_number}\n1234\n8.9\nOK\nError"
_mac_address = "EA-B2-41-27-7A-36"

_byte_content = _content.encode()


async def test_ZeverSolarFlowHandler_constructor():
    """Simple test for construction and initialization."""
    result_flow_handler = ZeverSolarFlowHandler()

    assert type(result_flow_handler) is ZeverSolarFlowHandler


async def test_ZeverSolarFlowHandler_async_step_user_user_input_is_none():
    """Tests the user step without valid user data."""
    result_flow_handler = ZeverSolarFlowHandler()

    my_flow_result = await result_flow_handler.async_step_user()

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "user"
    assert my_flow_result["errors"] == {}


async def test_ZeverSolarFlowHandler_async_step_user_user_input_id_loaded_new_inverter():
    """Tests the user step with user data and inverter is not configured yet."""
    result_flow_handler = ZeverSolarFlowHandler()

    data = {CONF_HOST: "TEST_HOST"}

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response
        with patch(
            "custom_components.zeversolar_local.config_flow.ZeverSolarFlowHandler._async_current_entries"
        ) as current_entries_mock:
            current_entries_mock.return_value = {}

            my_flow_result = await result_flow_handler.async_step_user(user_input=data)

    assert my_flow_result["type"] == "create_entry"


async def test_ZeverSolarFlowHandler_async_step_user_user_input_id_loaded_duplicate_inverter():
    """Tests the user step with user data and already configured inverter."""
    result_flow_handler = ZeverSolarFlowHandler()

    data = {CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: _mac_address}

    converter_entry_mock = MockConfigEntry(domain=DOMAIN, data=data)
    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response

        with patch(
            "custom_components.zeversolar_local.config_flow.ZeverSolarFlowHandler._async_current_entries"
        ) as method_mock:
            method_mock.return_value = {converter_entry_mock}
            my_flow_result = await result_flow_handler.async_step_user(user_input=data)

    assert my_flow_result["type"] == "abort"
    assert my_flow_result["reason"] == "duplicate_inverter"


async def test_ZeverSolarFlowHandler_async_step_user_user_input_id_other_inverter():
    """Tests the user step with user data and other configured inverter."""
    result_flow_handler = ZeverSolarFlowHandler()

    zever_inverter_id = "zever_inverter_id"
    zever_inverter_id2 = "zever_inverter_id_2"

    data = {CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: zever_inverter_id}

    converter_entry_mock = MockConfigEntry(domain=DOMAIN, data=data)
    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response

        with patch(
            "custom_components.zeversolar_local.config_flow.ZeverSolarFlowHandler._async_current_entries"
        ) as method_mock:
            method_mock.return_value = {converter_entry_mock}
            my_flow_result = await result_flow_handler.async_step_user(user_input=data)

    assert my_flow_result["type"] == "create_entry"


async def test_ZeverSolarFlowHandler_show_config_form():
    """Tests the config form method."""
    result_flow_handler = ZeverSolarFlowHandler()

    my_flow_result = await result_flow_handler._show_config_form()

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "user"
    assert my_flow_result["errors"] == {}


async def test_ZeverSolarFlowHandler_get_id():
    """Tests the _get_id method returning an id."""
    result_flow_handler = ZeverSolarFlowHandler()

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response
        result_id = await result_flow_handler._get_id("Test_host")

    assert result_id == _mac_address


async def test_ZeverSolarFlowHandler_test_url():
    """Tests the _test_url method returning an id."""
    result_flow_handler = ZeverSolarFlowHandler()

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response
        result = await result_flow_handler._test_url("Test_host")

    assert result


async def test_ZeverSolarFlowHandler_test_url_reacts_on_exception():
    """Tests the _test_url racting to an exception."""
    result_flow_handler = ZeverSolarFlowHandler()

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        api_mock.side_effect = Exception("text")
        result = await result_flow_handler._test_url("Test_host")

    assert not result


async def test_ZeverSolarFlowHandler_async_get_options_flow():
    """Tests the async_get_options_flow."""

    flow_handler = ZeverSolarFlowHandler()
    options_flow = OptionsFlow()

    result = flow_handler.async_get_options_flow(options_flow)

    assert type(result) is ZeverSolarOptionsFlowHandler


async def test_ZeverSolarOptionsFlowHandler_constructor():
    """Simple test for construction and initialization."""

    zever_inverter_id = "zever_id"

    data = {CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: zever_inverter_id}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = ZeverSolarOptionsFlowHandler(config_entry)

    assert type(options_flow_handler) is ZeverSolarOptionsFlowHandler


async def test_ZeverSolarOptionsFlowHandler_async_step_init_no_user_input():
    """Tests the init step without user input."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=None)

    options_flow_handler = ZeverSolarOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=None)

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "init"
    assert my_flow_result["errors"] == {}


async def test_ZeverSolarOptionsFlowHandler_async_step_init_user_input():
    """Tests the init step with valid user input."""
    data = {OPT_DATA_INTERVAL: 10}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = ZeverSolarOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=data)

    assert my_flow_result["type"] == "create_entry"


async def test_ZeverSolarOptionsFlowHandler_async_step_init_interval_empty():
    """Tests the init step with empty interval data."""
    data = {OPT_DATA_INTERVAL: None}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = ZeverSolarOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=data)

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "init"
    assert my_flow_result["errors"] == {"base": "data_interval_empty"}


async def test_ZeverSolarOptionsFlowHandler_async_step_init_interval_wrong():
    """Tests the init step with empty interval data."""
    data = {OPT_DATA_INTERVAL: 9}
    config_entry = MockConfigEntry(domain=DOMAIN, data=data)

    options_flow_handler = ZeverSolarOptionsFlowHandler(config_entry)

    my_flow_result = await options_flow_handler.async_step_init(user_input=data)

    assert my_flow_result["type"] == "form"
    assert my_flow_result["step_id"] == "init"
    assert my_flow_result["errors"] == {"base": "data_interval_wrong"}
