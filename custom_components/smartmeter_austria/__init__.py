"""The Smart Meter Austria integration."""

# Note for developers:
# vscode devcontainer.json has following entry:
# "runArgs": ["-e", "GIT_EDITOR=code --wait", "--device=/dev/ttyUSB0"]
# If the M-BUS to USB adapter is not present the docker image will not start.

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo
from smartmeter_austria_energy.smartmeter import Smartmeter
from smartmeter_austria_energy.supplier import SUPPLIERS

from .const import (
    CONF_COM_PORT,
    CONF_KEY_HEX,
    CONF_SUPPLIER_NAME,
    DOMAIN,
    OPT_DATA_INTERVAL,
    OPT_DATA_INTERVAL_VALUE,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .coordinator import SmartmeterDataCoordinator
from .smartmeter_data import SmartMeterData, SmartMeterConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: SmartMeterConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.debug(STARTUP_MESSAGE)

    # Set up the smart meter adapter from a config entry.
    supplier_name = entry.data.get(CONF_SUPPLIER_NAME)
    supplier = SUPPLIERS.get(supplier_name)
    port = entry.data.get(CONF_COM_PORT)
    key_hex = entry.data.get(CONF_KEY_HEX)

    data_interval = entry.options.get(
        OPT_DATA_INTERVAL, OPT_DATA_INTERVAL_VALUE)

    try:
        adapter = Smartmeter(supplier, port, key_hex)
        obisdata = await hass.async_add_executor_job(adapter.read)
    except Exception as err:
        raise ConfigEntryNotReady from err

    # Fetch data for the smart meter device
    device_number = obisdata.DeviceNumber.value
    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_number)},
        name=f"Smart Meter '{device_number}'",
    )

    # Create update coordinator
    coordinator = SmartmeterDataCoordinator(hass, adapter)
    coordinator.update_interval = timedelta(seconds=data_interval)
    coordinator.logger = _LOGGER

    # Fetch initial data so we have data when entities subscribe
    await coordinator.async_config_entry_first_refresh()

    # Store the deviceinfo and coordinator object for the platforms to access
    data = SmartMeterData(
        coordinator=coordinator, device_info=device_info, device_number=device_number)

    entry.runtime_data = data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Wait to install the reload listener until everything was successfully initialized
    entry.async_on_unload(entry.add_update_listener(
        async_options_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SmartMeterConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_options_update_listener(
    hass: HomeAssistant, config_entry: SmartMeterConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
