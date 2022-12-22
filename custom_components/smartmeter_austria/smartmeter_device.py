"""The Smart Meter Device."""
from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from smartmeter_austria_energy.smartmeter import Smartmeter

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import (
    ATTR_DEVICE_NAME,
    ATTR_FIRMWARE,
    ATTR_MODEL,
    ATTR_SERIAL_NUMBER,
    DEFAULT_DEVICE_NAME,
    DOMAIN,
    MANUFACTURER,
)

_LOGGER = logging.getLogger(__name__)


class SmartmeterEntity(Entity):
    """Representation of the smart meter as device."""

    def __init__(self, smartmeter: Smartmeter, data: Mapping[str, Any]) -> None:
        """Initialize the basic device."""
        self._data = data
        self.type = "device"
        self.smartmeter: Smartmeter = smartmeter
        self._available: bool = True

    @property
    def unique_id(self) -> str | None:
        """Return the unique id for this device."""
        if (serial := self._data.get(ATTR_SERIAL_NUMBER)) is None:
            return None
        return f"{serial}_{self.entity_description.key}"

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def device_info(self) -> DeviceInfo:
        """Return device specific attributes."""
        return {
            "identifiers": {(DOMAIN, self._data[ATTR_SERIAL_NUMBER])},
            "manufacturer": MANUFACTURER,
            "model": self._data[ATTR_MODEL],
            "name": self._data.get(ATTR_DEVICE_NAME, DEFAULT_DEVICE_NAME),
            "sw_version": self._data[ATTR_FIRMWARE],
        }
