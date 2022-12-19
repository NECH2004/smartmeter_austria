"""Test the coordinator classes."""
from unittest.mock import patch

from homeassistant.helpers.update_coordinator import UpdateFailed
import httpx
import pytest

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


async def test_zeversolarApiCoordinator_constructor(hass):
    """Simple test for construction and initialization."""
    api_client = ZeverSolarApiClient("TEST_HOST")
    result_coordinator = ZeversolarApiCoordinator(hass, api_client)

    assert type(result_coordinator) is ZeversolarApiCoordinator


async def test_zeversolarApiCoordinator_async_get_data_ok(hass):
    """Tests the async_get_data method returning data from the inverter."""
    api_client = ZeverSolarApiClient("TEST_HOST")
    result_coordinator = ZeversolarApiCoordinator(hass, api_client)

    with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
        mock_response = httpx.Response(
            200, request=httpx.Request("Get", "https://test.t"), content=_byte_content,
        )
        api_mock.return_value = mock_response

        result_data = await result_coordinator._async_update_data()

    assert result_data is not None
    assert result_coordinator.last_update_success


async def test_zeversolarApiCoordinator_async_get_data_exception(hass):
    """Tests the async_get_data method returning data from the inverter."""
    with pytest.raises(UpdateFailed):
        api_client = ZeverSolarApiClient("TEST_HOST")
        result_coordinator = ZeversolarApiCoordinator(hass, api_client)

        with patch("zever_local.inverter.httpx.AsyncClient.get") as api_mock:
            api_mock.side_effect = Exception("failure")
            await result_coordinator._async_update_data()
