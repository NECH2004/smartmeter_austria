"""The Smartmeter data coordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from smartmeter_austria_energy.exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from smartmeter_austria_energy.obisdata import ObisData
from smartmeter_austria_energy.smartmeter import Smartmeter

from .const import DOMAIN, OPT_DATA_INTERVAL_VALUE


_LOGGER = logging.getLogger(__name__)


class SmartmeterDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, adapter: Smartmeter) -> None:
        """Initialize."""
        self.adapter = adapter
        self.platforms = []

        super().__init__(
            # update_inverval is set in async_setup_entry()
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=OPT_DATA_INTERVAL_VALUE),
        )

    async def _async_update_data(self) -> ObisData:
        """Update data over the USB device."""
        try:
            self.last_update_success = True
            self.adapter.read()
            return self.adapter.obisData
        except SmartmeterTimeoutException as exception:
            self.logger.warn("smartmeter,read() timeout error. %s", exception)
            self.last_update_success = False
            raise UpdateFailed() from exception

        except SmartmeterSerialException as exception:
            self.logger.error("smartmeter,read() serial exception. %s", exception)
            self.last_update_success = False
            raise UpdateFailed() from exception

        except SmartmeterException as exception:
            self.logger.error("smartmeter,read() exception. %s", exception)
            self.last_update_success = False
            raise UpdateFailed() from exception

        except Exception as exception:
            self.logger.fatal("Zeversolar get_data() error. %s", exception)
            self.last_update_success = False
            raise UpdateFailed() from exception
