"""Tests for tmc_config.py."""

import pytest

from ska_mid_itf_engineering_tools.tmc_config.tmc_dish_ids import instance, instances, tmc_values


def test_instance_is_always_string():
    """Assert a string with SKA007 and one with SKA008 successfully returns as a string."""
    assert instance("SKA007") == "007", f"expected '007', instead received {instance('SKA007')}"
    assert instance("SKA008") == "008", f"expected '008', instead received {instance('SKA008')}"


def test_instance_list_is_always_string():
    """Assert a string with SKA007, SKA008 and SKA009 successfully returns as a string."""
    ids = "SKA007 SKA008 SKA009"
    assert instances(ids) == [
        "007",
        "008",
        "009",
    ], f"expected ['007', '008', '009'], instead received {instance(ids)}"


@pytest.mark.skip(reason="Skipping test in CI where dish IDs get overwritten")
def test_dish_values_is_string_list():
    """Assert a string with SKA007 and SKA008 populates the values dict with string indexes."""
    ids = "SKA007 SKA008"
    values = tmc_values(dish_ids=ids)
    dish_instances = values["ska-tmc-mid"]["deviceServers"]["dishleafnode"]["instances"]
    assert dish_instances == [
        "007",
        "008",
    ], f"expected ['007', '008'], instead received {dish_instances}"
