"""Tests for tmc_config.py."""

from ska_mid_itf_engineering_tools.tmc_config.tmc_dish_ids import instance


def test_instance_is_always_string():
    """Assert whether or not a string with SKA008 successfully returns as a string."""
    assert instance("SKA008") == "008", "expected '008', instead received " + instance("SKA008")
