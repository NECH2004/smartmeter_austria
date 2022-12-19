"""Test component setup."""
from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.exceptions import ConfigEntryNotReady
import httpx
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    MockModule,
    mock_integration,
)

from custom_components.zeversolar_local.__init__ import (
    async_options_update_listener,
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)
from custom_components.zeversolar_local.const import (  # ENTRY_DEVICE_INFO,
    CONF_SERIAL_NO,
    DOMAIN,
    ENTRY_COORDINATOR,
)
from custom_components.zeversolar_local.coordinator import ZeversolarApiCoordinator
from custom_components.zeversolar_local.zever_local import ZeverSolarApiClient

_registry_id = "EAB241277A36"
_registry_key = "ZYXTBGERTXJLTSVS"
_hardware_version = "M11"
_software_version = "18625-797R+17829-719R"
_time = "16:22"
_date = "20/02/2022"
_serial_number = "ZS150045138C0104"
_content = f"1\n1\n{_registry_id}\n{_registry_key}\n{_hardware_version}\n{_software_version}\n{_time} {_date}\n1\n1\n{_serial_number}\n1234\n8.9\nOK\nError"

_byte_content = _content.encode()


async def test_async_setup_entry_config_not_ready(hass):
    """Test the integration setup with no connection to the inverter throwning a ConfigEntryNotReady exception."""

    def side_effect_except():
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content
        )

        yield mock_response
        yield Exception("boo")

    with pytest.raises(ConfigEntryNotReady):
        mock_integration(hass, MockModule(DOMAIN))

        config_entry = MockConfigEntry(
            domain=DOMAIN,
            unique_id="my_unique_test_id",
            data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: "serial_no"},
        )

        config_entry.add_to_hass(hass)

        with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
            api_mock.side_effect = side_effect_except()

            await async_setup_entry(hass, config_entry)


async def test_async_setup_entry_domain_not_loaded(hass):
    """Test the integration setup with no domain data."""

    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: "serial_no"},
    )

    config_entry.add_to_hass(hass)

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response
        test_result = await async_setup_entry(hass, config_entry)
        assert test_result is True


async def test_async_setup_entry_domain_already_loaded(hass):
    """Test the integration setup with domain data."""

    hass.data.setdefault(DOMAIN, {})
    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: "serial_no"},
    )

    config_entry.add_to_hass(hass)

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response
        test_result = await async_setup_entry(hass, config_entry)
        assert test_result is True


async def test_async_setup_entry_domain_already_loaded_mock_coordinator(hass):
    """Test the integration setup with domain data."""

    hass.data.setdefault(DOMAIN, {})
    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: "serial_no"},
    )

    config_entry.add_to_hass(hass)

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response
        test_result = await async_setup_entry(hass, config_entry)

    assert test_result is True


async def test_async_unload_entry_all_can_be_unloaded(hass):
    """Test to unload the integration."""

    config_entry = MockConfigEntry(
        domain=DOMAIN, unique_id="my_unique_test_id", data={CONF_HOST: "TEST_HOST"}
    )

    client = ZeverSolarApiClient("HOST")
    coordinator = ZeversolarApiCoordinator(hass, client=client)

    mock_integration(hass, MockModule(DOMAIN))
    config_entry.add_to_hass(hass)
    hass.data.setdefault(
        DOMAIN, {config_entry.entry_id: {ENTRY_COORDINATOR: coordinator}}
    )

    test_result = await async_unload_entry(hass, config_entry)
    assert test_result is True


async def test_async_reload_entry(hass):
    """Test to relod the config entry."""

    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="my_unique_test_id",
        data={CONF_HOST: "TEST_HOST", CONF_SERIAL_NO: "serial_no"},
    )

    config_entry.add_to_hass(hass)

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response

        # must setup the entry first
        await async_setup_entry(hass, config_entry)

        # act
        await async_reload_entry(hass, config_entry)

    result_entry = hass.data[DOMAIN].pop(config_entry.entry_id)[ENTRY_COORDINATOR]

    # assert
    assert type(result_entry) is ZeversolarApiCoordinator


async def test_async_options_update_listener(hass):
    """Test the options update listener."""

    mock_integration(hass, MockModule(DOMAIN))

    config_entry = MockConfigEntry(
        domain=DOMAIN, unique_id="my_unique_test_id", data={CONF_HOST: "TEST_HOST"},
    )

    config_entry.add_to_hass(hass)

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload"
    ) as method_mock:
        # act
        await async_options_update_listener(hass, config_entry)

        # assert
        method_mock.assert_called_once()
