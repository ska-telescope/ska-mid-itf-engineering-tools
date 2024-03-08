"""."""

import logging
import os

from ska_ser_logging import configure_logging  # type: ignore
from yaml import safe_dump

logger = logging.getLogger(__name__)


def instance(x: str) -> str:
    """
    Create 2- or 3-character zero-padded integer string for DishID instance name.

    :param x: SKA DishID string
    :return: DishID for deviceserver instance name
    """
    return x[-3:]


def instances(ids: str = "SKA000") -> list[str]:
    """
    Create array of instances for deviceserver names.

    :param ids: space-separated string containing DishIDs, defaults to "SKA000"
    :return: Array of instances
    """
    ds_ids = list(ids.split(" "))
    instances = [instance(x) for x in ds_ids]
    return instances


def single_dish_id_uppercase(id: str = "SKA000") -> str:
    """
    Set DishID to uppercase for Tango device name.

    :param id: string representing DishID, defaults to "SKA000"
    :return: uppercase dishID
    """
    return id.upper()


def dish_ids_array_from_str(ids: str = "SKA000") -> list[str]:
    """
    Get Dish IDs in array form.

    :param ids: Space separated Dish IDs, defaults to "SKA000"
    :return: List of DishIDs
    """
    return list(ids.split(" "))


def set_cluster_domain(
    dish_id: str = "SKA000",
    domain_postfix: str = "miditf.internal.skao.int",
    domain_prefix: str = "",
) -> str:
    """
    Make wild assumptions about the future of Kubernetes clusters in SKAO.

    :param dish_id: Upper case DishID, defaults to "SKA000"
    :param domain_postfix: Cluster Domain where this dish is deployed, defaults to
        "miditf.internal.skao.int"
    :param domain_prefix: Prefix of Cluster Domain where this dish is deployed,
        defaults to ""
    :return: A cluster domain.
    """
    if domain_postfix == "miditf.internal.skao.int":
        return domain_postfix
    else:
        return domain_prefix + "." + dish_id + "." + domain_postfix


def dish_fqdns(
    hostname: str = "tango-databaseds",
    cluster_domain_postfix: str = "miditf.internal.skao.int",
    namespace_prefix: str = "dish-lmc-",
    dish_ids: str = "SKA000",
    namespace_postfix: str = "",
) -> list:
    """
    Create an array of Dish FQDNs for use by the TMC.

    See docstring for tmc_values() method.

    :param hostname: _description_, defaults to "tango-databaseds"
    :param cluster_domain_postfix: _description_, defaults to "miditf.internal.skao.int"
    :param namespace_prefix: _description_, defaults to "dish-lmc-"
    :param namespace_postfix: _description_, defaults to ""
    :param dish_ids: Space separated DishIDS, defaults to "SKA000"
    :return: list of addresses
    """
    arr_dish_ids = dish_ids_array_from_str(dish_ids)
    logger.debug(f"dish_ids: {arr_dish_ids}")

    def single_dish_fqdn(
        hostname: str = "tango-databaseds",
        cluster_domain_postfix: str = "miditf.internal.skao.int",
        namespace_prefix: str = "dish-lmc-",
        dish_id: str = "SKA000",
        namespace_postfix: str = "",
    ) -> str:
        id = single_dish_id_uppercase(id=dish_id)
        cluster_domain = set_cluster_domain(dish_id=id, domain_postfix=cluster_domain_postfix)
        return f"tango://{hostname}.{namespace_prefix}{id}{namespace_postfix}.svc.{cluster_domain}:10000/mid-dish/dish-manager/{id}"  # noqa E501

    fqdns = [
        single_dish_fqdn(
            hostname=hostname,
            cluster_domain_postfix=cluster_domain_postfix,
            namespace_prefix=namespace_prefix,
            namespace_postfix=namespace_postfix,
            dish_id=x,
        )
        for x in dish_ids_array_from_str(dish_ids)
    ]
    return fqdns


def tmc_values(
    hostname: str = "tango-databaseds",
    cluster_domain_postfix: str = "miditf.internal.skao.int",
    namespace_prefix: str = "dish-lmc-",
    dish_ids: str = "SKA000",
    namespace_postfix: str = "",
) -> dict:
    """
    Generate values for the TMC to connect to DishIDs as set in the environment.

    The environment variable DISH_IDS must be set in order for the TMC to connect to the
    correct Dishes.

    The namespace prefix for the DishLMC deployments will likely not differ between
    Dishes, but is useful for distinguishing between dev, testing and production
    namespaces. May be discarded at a later stage, but the default can be used as is in
    Production.

    The Cluster Domain will differ between dishes, as each Dish contains a Kubernetes
    cluster. For dishLMC deployments in the Mid ITF cluster the cluster domain remains
    the same.

    Hostname is being standardised on and may not be a parameter later on. Default
    should be used in production.

    :param hostname: TangoDB hostname, defaults to "tango-databaseds"
    :param cluster_domain_postfix: Cluster Domain prefix for each dish, defaults to
        "miditf.internal.skao.int" for MidITF cluster
    :param namespace_prefix: _description_, defaults to "dish-lmc-"
    :param namespace_postfix: _description_, defaults to ""
    :param dish_ids: _description_, defaults to "SKA000"
    :return: dict with values
    """
    if "DISH_IDS" in os.environ:
        dish_ids = os.environ["DISH_IDS"]
    if "TANGO_DATABASE_DS" in os.environ:
        hostname = os.environ["TANGO_DATABASE_DS"]
    if "CLUSTER_DOMAIN_POSTFIX" in os.environ:
        cluster_domain_postfix = os.environ["CLUSTER_DOMAIN_POSTFIX"]
    if "KUBE_NAMESPACE_PREFIX" in os.environ:
        namespace_prefix = os.environ["KUBE_NAMESPACE_PREFIX"]
    if "KUBE_NAMESPACE_POSTFIX" in os.environ:
        namespace_postfix = os.environ["KUBE_NAMESPACE_POSTFIX"]
    values = {
        "tmc": {
            "deviceServers": {
                "centralnode": {"DishIDs": dish_ids_array_from_str(dish_ids)},
                "subarraynode": {"DishIDs": dish_ids_array_from_str(dish_ids)},
                "dishleafnode": {"instances": instances(dish_ids)},
            },
            "global": {
                "namespace_dish": {
                    "dish_name": dish_fqdns(
                        hostname=hostname,
                        cluster_domain_postfix=cluster_domain_postfix,
                        namespace_prefix=namespace_prefix,
                        dish_ids=dish_ids,
                        namespace_postfix=namespace_postfix,
                    )
                }
            },
        }
    }
    return values


def main() -> None:
    """Create tmc-values.yaml file in $SUT_CHART_DIR folder for TMC to use."""
    assert "SUT_CHART_DIR" in os.environ, "SUT_CHART_DIR environment variable not set"

    configure_logging(logging.DEBUG)
    values = tmc_values()
    chart_dir = os.environ["SUT_CHART_DIR"]
    values_file_path = os.path.join(chart_dir, "tmc-values.yaml")
    logger.debug(f"values_file_path: {values_file_path}")
    with open(values_file_path, "w") as file:
        safe_dump(values, file)


if __name__ == "__main__":
    assert (
        "CLUSTER_DOMAIN_POSTFIX" in os.environ
    ), "CLUSTER_DOMAIN_POSTFIX environment variable not set."
    assert "DISH_IDS" in os.environ, "DISH_IDS environment variable not set."
    main()
