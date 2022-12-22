"""Constants for the Smartmeter Austria Energy integration."""
from homeassistant.const import Platform

DOMAIN = "smartmeter_austria_energy"

DEFAULT_INTEGRATION_TITLE = "Smartmeter Austria"
DEFAULT_DEVICE_NAME = "Smart Meter"

DEVICES = "devices"
MANUFACTURER = "TEST_MANUFACTURER"

ATTR_DEVICE_NAME = "device_name"
ATTR_DEVICE_ID = "device_id"
ATTR_SERIAL_NUMBER = "serial_number"
ATTR_MODEL = "model"
ATTR_FIRMWARE = "firmware"

# Base component constants
NAME = "Smart Meter Austria Integration"
DEVICE_NAME = "Smart meter"
DEVICE_MODEL = "Smart meter"
MANUFACTURER_NAME = "a manufacturer"

ISSUE_URL = "https://github.com/nech/smartmeter_austria/issues"

DOMAIN_DATA = f"{DOMAIN}_data"

# Config entries
CONF_SUPPLIER_NAME = "supplier"
CONF_SERIAL_NO = "smartmeter_aut_serial_number"
CONF_COM_PORT = "com_port"
CONF_KEY_HEX = "key_hex"


ENTRY_COORDINATOR = "smartmeter_aut_coordinator"
ENTRY_DEVICE_INFO = "smartmeter_aut_device_info"

OPT_DATA_INTERVAL = "smartmeter_aut_data_interval"
OPT_DATA_INTERVAL_VALUE: int = 30


"""List of platforms that are supported."""
PLATFORMS = [Platform.SENSOR]

# Additional
"""The actual version of the integration."""
VERSION = "1.0.2"

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
Fetch data from an Austrian smart meter using its M-BUS interface.
This is a custom integration!
If you have any issues with this integration, please open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
