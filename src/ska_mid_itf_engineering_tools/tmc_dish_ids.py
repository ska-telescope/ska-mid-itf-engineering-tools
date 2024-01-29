"""."""
import os

from yaml import safe_dump


def instance(x: str) -> str:
    """Create two- or three-character zero-padded integer string for DishID instance name.

    :param x: SKA DishID string
    :type x: str
    :return: DishID for deviceserver instance name
    :rtype: str
    """
    return x[-3:]


def instances(ids: str = "SKA000") -> list[str]:
    """Create array of instances for deviceserver names.

    :param ids: space-separated string containing DishIDs, defaults to "SKA000"
    :type ids: str
    :return: Array of instances
    :rtype: list[str]
    """
    ds_ids = list(ids.split(" "))
    instances = [instance(x) for x in ds_ids]
    return instances


def single_dish_id_lowercase(id: str = "SKA000") -> str:
    """Set DishID to lowercase for Tango device name.

    :param id: string representing DishID, defaults to "SKA000"
    :type id: str
    :return: lowercase dishID
    :rtype: str
    """
    return id.lower()


def dish_ids_array_from_str(ids: str = "SKA000") -> list[str]:
    """Get Dish IDs in array form.

    :param ids: Space separated Dish IDs, defaults to "SKA000"
    :type ids: str
    :return: List of DishIDs
    :rtype: list[str]
    """
    return list(ids.split(" "))


def set_cluster_domain(
    dish_id: str = "ska000",
    domain_postfix: str = "miditf.internal.skao.int",
    domain_prefix: str = "",
):
    """Make wild assumptions about the future of Kubernetes clusters in SKAO.

    :param dish_id: Lowercase DishID, defaults to "ska000"
    :type dish_id: str
    :param domain_postfix: Cluster Domain where this dish is deployed, defaults to
        "miditf.internal.skao.int"
    :type domain_postfix: str
    :param domain_prefix: Prefix of Cluster Domain where this dish is deployed, defaults to
        ""
    :type domain_prefix: str
    :return: A cluster domain.
    :rtype: str
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
):
    """Create an array of Dish FQDNs for use by the TMC.

    See docstring for tmc_values() method.

    :param hostname: _description_, defaults to "tango-databaseds"
    :type hostname: str
    :param cluster_domain_postfix: _description_, defaults to "miditf.internal.skao.int"
    :type cluster_domain_postfix: str
    :param namespace_prefix: _description_, defaults to "dish-lmc-"
    :type namespace_prefix: str
    :param namespace_postfix: _description_, defaults to ""
    :type namespace_postfix: str
    :param dish_ids: Space separated DishIDS, defaults to "SKA000"
    :type dish_ids: str
    :return: _description_
    :rtype: _type_
    """
    arr_dish_ids = dish_ids_array_from_str(dish_ids)
    print(arr_dish_ids)

    def single_dish_fqdn(
        hostname: str = "tango-databaseds",
        cluster_domain_postfix: str = "miditf.internal.skao.int",
        namespace_prefix: str = "dish-lmc-",
        dish_id: str = "SKA000",
        namespace_postfix: str = "",
    ):
        id = single_dish_id_lowercase(id=dish_id)
        cluster_domain = set_cluster_domain(dish_id=id, domain_postfix=cluster_domain_postfix)
        return f"tango://{hostname}.{namespace_prefix}{id}{namespace_postfix}.svc.{cluster_domain}:10000/{id}/elt/master"  # noqa E501

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
    hostname="tango-databaseds",
    cluster_domain_postfix="miditf.internal.skao.int",
    namespace_prefix="dish-lmc-",
    dish_ids="SKA000",
    namespace_postfix: str = "",
):
    """Generate values for the TMC to connect to DishIDs as set in the environment.

    The environment variable DISH_IDS must be set in order for the TMC to connect to the
    correct Dishes.

    The namespace prefix for the DishLMC deployments will likely not differ between
    Dishes, but is useful for distinguishing between dev, testing and production namespaces.
    May be discarded at a later stage, but the default can be used as is in Production.

    The Cluster Domain will differ between dishes, as each Dish contains a Kubernetes cluster.
    For dishLMC deployments in the Mid ITF cluster the cluster domain remains the same.

    Hostname is being standardised on and may not be a parameter later on. Default should be used
    in Production.

    :param hostname: TangoDB hostname, defaults to "tango-databaseds"
    :type hostname: str, optional
    :param cluster_domain_postfix: Cluster Domain prefix for each dish, defaults to
        "miditf.internal.skao.int" for MidITF cluster
    :type cluster_domain_postfix: str, optional
    :param namespace_prefix: _description_, defaults to "dish-lmc-"
    :type namespace_prefix: str, optional
    :param namespace_postfix: _description_, defaults to ""
    :type namespace_postfix: str
    :param dish_ids: _description_, defaults to "SKA000"
    :type dish_ids: str, optional
    :return: _description_
    :rtype: _type_
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


def main():
    """Create tmc-values.yaml file in charts/system-under-test folder for TMC to use."""
    values = tmc_values()
    cur = os.path.dirname(os.path.abspath(__file__))
    with open(
        os.path.join(cur, "..", "..", "charts", "system-under-test", "tmc-values.yaml"),
        "w",
    ) as file:
        safe_dump(values, file)


if __name__ == "__main__":
    assert (
        "CLUSTER_DOMAIN_POSTFIX" in os.environ
    ), "CLUSTER_DOMAIN_POSTFIX environment variable not set."
    assert "DISH_IDS" in os.environ, "DISH_IDS environment variable not set."
    # print(os.environ)
    main()
