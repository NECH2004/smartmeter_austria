"""Sensor tests."""
from unittest.mock import patch

from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
import httpx
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from zever_local.inverter import Inverter

from custom_components.zeversolar_local.button import (
    ZeverSolarButton,
    ZeversolarButtonEntityDescription,
    async_setup_entry,
)
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


def async_add_entities(entities):
    """Add entities to a sensor as simuation for unit test. Helper method."""
    count = entities.__len__()
    assert count == 2


async def test_async_setup_entry(hass):
    """Tests the setup of the button platform."""
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

    await async_setup_entry(hass, config_entry, async_add_entities)


async def test_ZeverSolarButton_class():
    """Simple test for construction and initialization."""
    address = "10.10.10.1"
    inverter = Inverter(address)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, inverter.serial_number)},
        name=f"ZeverSolar inverter '{inverter.serial_number}'",
        manufacturer="ZeverSolar",
        hw_version="M10",
        sw_version="17717-709R+17511-707R",
    )

    entity_description = ZeversolarButtonEntityDescription(
        key="power_on",
        name="Power On",
        press_action=lambda device: device.power_on(),
        icon="mdi:power-cycle",
    )

    result_button = ZeverSolarButton(inverter, device_info, entity_description)
    assert isinstance(result_button, ZeverSolarButton)


async def test_ZeverSolarButton_press_button():
    """Simple test for construction and initialization."""
    address = "10.10.10.1"
    inverter = Inverter(address)

    device_info = DeviceInfo(
        identifiers={(DOMAIN, inverter.serial_number)},
        name=f"ZeverSolar inverter '{inverter.serial_number}'",
        manufacturer="ZeverSolar",
        hw_version="M10",
        sw_version="17717-709R+17511-707R",
    )

    entity_description = ZeversolarButtonEntityDescription(
        key="power_on",
        name="Power On",
        press_action=lambda device: device.power_on(),
        icon="mdi:power-cycle",
    )

    result_button = ZeverSolarButton(inverter, device_info, entity_description)
    with patch("zever_local.inverter.httpx.AsyncClient.post") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t")
        )
        api_mock.return_value = mock_response

        await result_button.async_press()
