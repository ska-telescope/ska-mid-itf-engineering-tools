"""Tests for verifying correct DishID generation."""

import os

import pytest
from yaml import safe_load

from ska_mid_itf_engineering_tools.tmc_config.tmc_dish_ids import (
    dish_fqdns,
    dish_ids_array_from_str,
    tmc_values,
)

DISH_IDS = "SKA001 SKA036 SKA063 SKA100"
os.environ["DISH_IDS"] = DISH_IDS


@pytest.fixture
def tmc_dishes_1() -> dict:
    """Fixture for testing.

    :return: Data ready to dump in TMC values.yaml
    :rtype: dict
    """
    return tmc_values(dish_ids=DISH_IDS)


@pytest.fixture
def tmc_dishes() -> dict:
    """Load Yaml file with DishIDs for AA0.5.

    :return: tmc_dishes: a dict with all the DishID info
    :rtype: dict
    """
    cur = os.path.dirname(os.path.abspath(__file__))
    with open(
        os.path.join(cur, "tmc-values.yaml"),
        "r",
    ) as file:
        dishes = safe_load(file)
    return dishes


def test_dish_ids_array_from_str() -> None:
    """Test correct Dish Array is generated from space separated string."""
    assert dish_ids_array_from_str(DISH_IDS) == ["SKA001", "SKA036", "SKA063", "SKA100"], (
        f"Expected array of str:\n{['SKA001', 'SKA036', 'SKA063', 'SKA100']}\n"
        f"Instead received:\n {dish_ids_array_from_str(DISH_IDS)}"
    )

    assert dish_ids_array_from_str(ids="SKA000 SKA001") == ["SKA000", "SKA001"], (
        f"Expected array of str:\n{['SKA000', 'SKA001']}\nInstead received:\n"
        "{dish_ids_array_from_str(ids='SKA000 SKA001')}"
    )

    assert dish_ids_array_from_str(ids="SKA000") == ["SKA000"], (
        f"Expected array of str:\n{['SKA000']}\nInstead received:\n"
        "{dish_ids_array_from_str(ids='SKA000')}"
    )


def test_instances(tmc_dishes: dict, tmc_dishes_1: dict) -> None:
    """Ensure that the instances are correctly set for DishLeafnode.

    :param tmc_dishes: Pytest Fixture
    :type tmc_dishes: dict
    :param tmc_dishes_1: Fixture data
    :type tmc_dishes_1: dict
    """
    assert (
        tmc_dishes["ska-tmc-mid"]["deviceServers"]["dishleafnode"]["instances"]
        == tmc_dishes_1["ska-tmc-mid"]["deviceServers"]["dishleafnode"]["instances"]
    ), (
        f"ERROR:\nExpected: "
        f"{tmc_dishes['ska-tmc-mid']['deviceServers']['dishleafnode']['instances']}\n "
        f"Actual:\n{tmc_dishes_1['ska-tmc-mid']['deviceServers']['dishleafnode']['instances']}"
    )
    assert (
        tmc_dishes["ska-tmc-mid"]["deviceServers"]["dishleafnode"]["instances"]
        == tmc_dishes_1["ska-tmc-mid"]["deviceServers"]["dishleafnode"]["instances"]
    ), (
        f"ERROR:\nExpected: "
        f"{tmc_dishes['ska-tmc-mid']['deviceServers']['dishleafnode']['instances']}\n"
        f"Actual:\n{tmc_dishes_1['ska-tmc-mid']['deviceServers']['dishleafnode']['instances']}"
    )


def test_dish_fqnds() -> None:
    """Ensure that FQDNs are correctly generated for TMC."""
    the_domain = "svc.miditf.internal.skao.int"
    the_dish_ids = [
        f"tango://tango-databaseds.dish-lmc-ska001.{the_domain}:"
        "10000/mid-dish/dish-manager/SKA001",
        f"tango://tango-databaseds.dish-lmc-ska036.{the_domain}:"
        "10000/mid-dish/dish-manager/SKA036",
        f"tango://tango-databaseds.dish-lmc-ska063.{the_domain}:"
        "10000/mid-dish/dish-manager/SKA063",
        f"tango://tango-databaseds.dish-lmc-ska100.{the_domain}:"
        "10000/mid-dish/dish-manager/SKA100",
    ]
    assert (
        dish_fqdns(dish_ids=DISH_IDS) == the_dish_ids
    ), f"Expected array of strings {the_dish_ids}"


def test_values_dict(tmc_dishes: dict, tmc_dishes_1: dict) -> None:
    """Ensure correct data is generated for storage in tmc-values.yaml file.

    :param tmc_dishes: Pytest Fixture
    :type tmc_dishes: dict
    :param tmc_dishes_1: Fixture data
    :type tmc_dishes_1: dict
    """
    assert (
        tmc_dishes == tmc_dishes_1
    ), f"Output not as expected: was expecting\n{tmc_dishes}\ninstead got\n{tmc_dishes_1}"
