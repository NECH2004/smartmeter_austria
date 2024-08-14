"""Defines a config entry data class."""
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import SmartmeterDataCoordinator


@dataclass
class SmartMeterData:
    """Defines smart meter Austria data class."""

    def __init__(self, coordinator: SmartmeterDataCoordinator, device_info: DeviceInfo, device_number: str) -> None:
        """Initialize."""
        self._coordinator = coordinator
        self._device_info = device_info
        self._device_number = device_number

    @property
    def coordinator(self) -> str:
        """Gets the coordinator."""
        return self._coordinator

    @property
    def device_info(self) -> str:
        """Gets the device info."""
        return self._device_info

    @property
    def device_number(self) -> str:
        """Gets the device number."""
        return self._device_number


# The type alias needs to be suffixed with 'ConfigEntry'
type SmartMeterConfigEntry = ConfigEntry[SmartMeterData]
