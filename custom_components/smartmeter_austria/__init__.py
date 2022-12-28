"""The Smart Meter Austria integration."""

# Note for developers:
# vscode devcontainer.json has following entry:
# "runArgs": ["-e", "GIT_EDITOR=code --wait", "--device=/dev/ttyUSB0"]
# If the M-BUS to USB adapter is not present the docker image will not start.

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo

from smartmeter_austria_energy.smartmeter import Smartmeter

from .const import (
    CONF_SUPPLIER_NAME,
    CONF_COM_PORT,
    CONF_KEY_HEX,
    DOMAIN,
    ENTRY_COORDINATOR,
    ENTRY_DEVICE_INFO,
    ENTRY_DEVICE_NUMBER,
    OPT_DATA_INTERVAL,
    OPT_DATA_INTERVAL_VALUE,
    PLATFORMS,
    STARTUP_MESSAGE,
)

from .coordinator import SmartmeterDataCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    # Set up the smart meter adapter from a config entry.
    supplier_name = entry.data.get(CONF_SUPPLIER_NAME)
    port = entry.data.get(CONF_COM_PORT)
    key_hex = entry.data.get(CONF_KEY_HEX)

    data_interval = entry.options.get(OPT_DATA_INTERVAL, OPT_DATA_INTERVAL_VALUE)

    adapter = Smartmeter(supplier_name, port, key_hex)

    try:
        adapter.read()
        obisdata = adapter.obisData

        coordinator = SmartmeterDataCoordinator(hass, adapter)
        coordinator.update_interval = timedelta(seconds=data_interval)
        await coordinator.async_refresh()

        if not coordinator.last_update_success:
            raise ConfigEntryNotReady

    except Exception as err:
        raise ConfigEntryNotReady from err

    device_number = obisdata.DeviceNumber.Value

    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_number)},
        name=f"Smart Meter '{device_number}'",
        has_entity_name=True,
    )

    # Store the deviceinfo and coordinator object for the platforms to access
    hass.data[DOMAIN][entry.entry_id] = {
        ENTRY_COORDINATOR: coordinator,
        ENTRY_DEVICE_INFO: device_info,
        ENTRY_DEVICE_NUMBER: device_number,
    }

    for platform in PLATFORMS:
        coordinator.platforms.append(platform)
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    # Wait to install the reload listener until everything was successfully initialized
    entry.async_on_unload(entry.add_update_listener(async_options_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id][ENTRY_COORDINATOR]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_options_update_listener(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
