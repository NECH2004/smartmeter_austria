"""Config flow for Smart meter integration."""
from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
import serial.tools.list_ports
from smartmeter_austria_energy.exceptions import SmartmeterException
from smartmeter_austria_energy.smartmeter import Smartmeter
from smartmeter_austria_energy.supplier import SUPPLIERS
import voluptuous as vol

from .const import (
    CONF_COM_PORT,
    CONF_KEY_HEX,
    CONF_SERIAL_NO,
    CONF_SUPPLIER_NAME,
    DOMAIN,
    OPT_DATA_INTERVAL,
    OPT_DATA_INTERVAL_VALUE,
)

_LOGGER = logging.getLogger(__name__)


def validate_and_connect(data: Mapping[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect."""
    com_port = data[CONF_COM_PORT]
    supplier_name = data[CONF_SUPPLIER_NAME]
    key_hex = data[CONF_KEY_HEX]

    _LOGGER.debug("Initialising com port=%s", com_port)
    ret = {}
    try:
        supplier = SUPPLIERS.get(supplier_name)
        adapter = Smartmeter(supplier, com_port, key_hex)
        obisdata = adapter.read()

        device_number = obisdata.DeviceNumber.value
        ret["title"] = f"Smart Meter '{device_number}'"
        ret["device_number"] = device_number
        _LOGGER.debug("Returning device info=%s", ret)
    except SmartmeterException as err:
        _LOGGER.warning("Could not connect to device=%s", com_port)
        raise err

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
    _LOGGER.warning(
        "No com ports found.  Need a valid M-BUS to USB device to communicate"
    )
    return None, None


class SmartmeterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the smart meters."""

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
                    validate_and_connect, user_input
                )

            except SmartmeterException:
                return self.async_abort(reason="cannot_connect")
            else:
                info.update(user_input)

                device_unique_id = info["device_number"]
                await self.async_set_unique_id(device_unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_SUPPLIER_NAME: user_input[CONF_SUPPLIER_NAME],
                        CONF_COM_PORT: user_input[CONF_COM_PORT],
                        CONF_KEY_HEX: user_input[CONF_KEY_HEX],
                        CONF_SERIAL_NO: device_unique_id,
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
        }
        schema = vol.Schema(config_options)

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return SmartMeterOptionsFlowHandler(config_entry)


class SmartMeterOptionsFlowHandler(config_entries.OptionsFlow):
    """Defines the configurable options for a smart meter."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            new_data_interval = user_input[OPT_DATA_INTERVAL]
            _LOGGER.debug("New data interval was set to %s", new_data_interval)

            if new_data_interval is None:
                _LOGGER.debug("New data interval is none")
                _errors["base"] = "data_interval_empty"

            elif not 5 <= new_data_interval <= 3600:
                _LOGGER.debug("New data interval is wrong (out of limits)")
                _errors["base"] = "data_interval_wrong"

            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        OPT_DATA_INTERVAL,
                        default=self.config_entry.options.get(
                            OPT_DATA_INTERVAL, OPT_DATA_INTERVAL_VALUE
                        ),
                    ): int,
                }
            ),
            errors=_errors,
        )
