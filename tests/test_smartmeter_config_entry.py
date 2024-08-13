"""Tests the smartmeter config entry."""
from custom_components.smartmeter_austria.smartmeter_config_entry import SmartMeterConfigEntry


def test_SmartMeterConfigEntry_constructor():
    """Simple test for device config construction and initialization."""
    result = SmartMeterConfigEntry(
        coordinator=None, device_info=None, device_number=None)

    assert isinstance(result, SmartMeterConfigEntry)


def test_SmartMeterConfigEntry_properties():
    """Simple test for smart meter config properties."""

    foo: str = "test"

    result = SmartMeterConfigEntry(
        coordinator=None, device_info=None, device_number=foo)

    assert result.coordinator is None
    assert result.device_info is None
    assert result.device_number == foo
