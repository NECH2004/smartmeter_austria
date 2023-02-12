"""The Smartmeter data coordinator."""
from __future__ import annotations

import asyncio
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


class SmartmeterDataCoordinator(DataUpdateCoordinator[ObisData]):
    """Fetches the data from the serial device."""

    def __init__(self, hass: HomeAssistant, adapter: Smartmeter) -> None:
        """Initialize."""
        self.adapter: Smartmeter = adapter
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
            obisdata = await self.hass.async_add_executor_job(self.adapter.read)
            return obisdata
        except SmartmeterTimeoutException as exception:
            self.logger.warning(
                "smartmeter.read() timeout error. %s", exception, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(10)
            raise UpdateFailed() from exception

        except SmartmeterSerialException as exception:
            self.logger.warning(
                "smartmeter.read() serial exception. %s", exception, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(10)
            raise UpdateFailed() from exception

        except SmartmeterException as exception:
            self.logger.warning(
                "smartmeter.read() smartmeter exception. %s", exception, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(10)
            raise UpdateFailed() from exception

        except Exception as exception:
            self.logger.error(
                "smartmeter.read() exception. %s", exception, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(30)
            raise UpdateFailed() from exception
