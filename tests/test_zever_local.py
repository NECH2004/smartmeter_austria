"""Tests the ZeverSolar API wrapper."""
from unittest.mock import patch

import httpx

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


async def test_ZeverSolarApiClient_class(hass):
    """Simple test for construction and initialization."""
    host = "TEST_HOST"

    result_api = ZeverSolarApiClient(host)
    assert type(result_api) is ZeverSolarApiClient


async def test_ZeverSolarApiClient_async_get_id_ok(hass):
    """Simple test for construction and initialization."""
    host = "TEST_HOST"

    result_api = ZeverSolarApiClient(host)

    mock_response = httpx.Response(
        200, request=httpx.Request("Get", f"https://{host}"), content=_byte_content
    )

    with patch("zever_local.inverter.httpx.AsyncClient.get") as mock_device_info:
        mock_device_info.return_value = mock_response

        expected_id = "EA-B2-41-27-7A-36"
        result_id = await result_api.async_get_id()

        assert expected_id == result_id


async def test_ZeverSolarApiClient_async_get_data_ok(hass):
    """Simple test for construction and initialization."""
    host = "TEST_HOST"

    result_api = ZeverSolarApiClient(host)

    mock_response = httpx.Response(
        200, request=httpx.Request("Get", f"https://{host}"), content=_byte_content
    )

    with patch("zever_local.inverter.httpx.AsyncClient.get") as mock_device_info:
        mock_device_info.return_value = mock_response

        inverter_data = await result_api.async_get_data()

    energy_today_KWh = inverter_data.energy_today_KWh
    assert energy_today_KWh == 8.09
