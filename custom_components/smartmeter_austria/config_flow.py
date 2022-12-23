"""Config flow for Smart meter integration."""
from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

import serial.tools.list_ports
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from homeassistant.data_entry_flow import FlowResult

from smartmeter_austria_energy.smartmeter import Smartmeter
from smartmeter_austria_energy.supplier import SUPPLIERS
from smartmeter_austria_energy.exceptions import SmartmeterException

from .const import CONF_SUPPLIER_NAME, CONF_COM_PORT, CONF_KEY_HEX, DOMAIN

_LOGGER = logging.getLogger(__name__)


def validate_and_connect(
    hass: core.HomeAssistant, data: Mapping[str, Any]
) -> dict[str, str]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    com_port = data[CONF_COM_PORT]
    supplier = data[CONF_SUPPLIER_NAME]
    key_hex = data[CONF_KEY_HEX]

    _LOGGER.debug("Initialising com port=%s", com_port)
    ret = {}
    ret["title"] = "Title hugo"
    try:
        client = Smartmeter(supplier, com_port, key_hex)
        client.read()
        obisdata = client.obisData
        # ret[ATTR_MODEL] = f"{client.version()} ({client.pn()})"
        _LOGGER.info("Returning device info=%s", ret)
    except SmartmeterException as err:
        _LOGGER.warning("Could not connect to device=%s", com_port)
        raise err
    finally:
        client.close()

    # Return info we want to store in the config entry.
    return ret


def scan_comports() -> tuple[list[str] | None, str | None]:
    """Find and store available com ports for the GUI dropdown."""
    com_ports = serial.tools.list_ports.comports(include_links=True)
    com_ports_list = []
    for port in com_ports:
        com_ports_list.append(port.device)
        _LOGGER.debug("COM port option: %s", port.device)
    if len(com_ports_list) > 0:
        return com_ports_list, com_ports_list[0]
    _LOGGER.warning("No com ports found.  Need a valid RS485 device to communicate")
    return None, None


class SmartmeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aurora ABB PowerOne."""

    VERSION = 1

    def __init__(self):
        """Initialise the config flow."""
        self.config = None
        self._com_ports_list = None
        self._default_com_port = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialised by the user."""

        errors = {}
        if self._com_ports_list is None:
            result = await self.hass.async_add_executor_job(scan_comports)
            self._com_ports_list, self._default_com_port = result
            if self._default_com_port is None:
                return self.async_abort(reason="no_serial_ports")

        # Handle the initial step.
        if user_input is not None:
            try:
                info = await self.hass.async_add_executor_job(
                    validate_and_connect, self.hass, user_input
                )
            except SmartmeterException:
                errors["base"] = "cannot_connect"
            else:
                info.update(user_input)
                # Bomb out early if someone has already set up this device.
                # device_unique_id = info["serial_number"]
                # await self.async_set_unique_id(device_unique_id)
                # self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_SUPPLIER_NAME: user_input[CONF_SUPPLIER_NAME],
                        CONF_COM_PORT: user_input[CONF_COM_PORT],
                        CONF_KEY_HEX: user_input[CONF_KEY_HEX],
                    },
                )

        # If no user input, must be first pass through the config.  Show  initial form.
        suppliers = list(SUPPLIERS.keys())
        default_supplier = suppliers[0]

        config_options = {
            vol.Required(CONF_SUPPLIER_NAME, default=default_supplier): SelectSelector(
                SelectSelectorConfig(
                    options=suppliers, mode=SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(CONF_COM_PORT, default=self._default_com_port): SelectSelector(
                SelectSelectorConfig(
                    options=self._com_ports_list, mode=SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(CONF_KEY_HEX): str,
            # vol.Required(CONF_ADDRESS, default=DEFAULT_ADDRESS): vol.In(range(MIN_ADDRESS, MAX_ADDRESS + 1)),
        }
        schema = vol.Schema(config_options)

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
