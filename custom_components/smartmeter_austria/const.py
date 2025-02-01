"""Constants for the Smartmeter Austria Energy integration."""
from homeassistant.const import Platform

DOMAIN = "smartmeter_austria"

# Base component constants
NAME = "Smart Meter Austria Integration"
ISSUE_URL = "https://github.com/NECH2004/smartmeter_austria/issues"

# Config entries
CONF_SUPPLIER_NAME = "supplier"
CONF_SERIAL_NO = "smartmeter_aut_serial_number"
CONF_COM_PORT = "com_port"
CONF_KEY_HEX = "key_hex"

OPT_DATA_INTERVAL = "smartmeter_aut_data_interval"
OPT_DATA_INTERVAL_VALUE: int = 30


"""List of platforms that are supported."""
PLATFORMS = [Platform.SENSOR]

# Additional
"""The actual version of the integration."""
VERSION = "1.4.11"

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
