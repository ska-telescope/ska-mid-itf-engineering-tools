"""
Test tangoctl options.

# type: ignore[import-untyped]
"""

import logging
import os
from typing import Any

from ska_mid_itf_engineering_tools.tango_control.read_tango_devices import (
    TangoctlDevices,
    TangoctlDevicesBasic,
)

logging.basicConfig(level=logging.WARNING)
_module_logger = logging.getLogger("test_tango_control")
_module_logger.setLevel(logging.WARNING)


def test_configuration_data(configuration_data: dict) -> None:
    """
    Check configuration data file.

    :param configuration_data: tangoctl setup
    """
    assert len(configuration_data) > 0


def test_tango_host(
    configuration_data: dict, kube_namespace: str, tango_control_handle: Any
) -> None:
    """
    Test that Tango database is up and running.

    :param configuration_data: tangoctl setup
    :param kube_namespace: K8S namespace
    :param tango_control_handle: instance of Tango control class
    """
    databaseds_name: str = configuration_data["databaseds_name"]
    cluster_domain: str = configuration_data["cluster_domain"]
    databaseds_port: int = configuration_data["databaseds_port"]

    tango_fqdn = f"{databaseds_name}.{kube_namespace}.svc.{cluster_domain}"
    tango_host = f"{tango_fqdn}:{databaseds_port}"

    _module_logger.info("Use Tango host %s", tango_host)

    os.environ["TANGO_HOST"] = tango_host
    _module_logger.info("Set TANGO_HOST to %s", tango_host)

    rv = tango_control_handle.check_tango(tango_fqdn, True)
    assert rv == 0


def test_read_input_files(tango_control_handle: Any) -> None:
    """
    Check input files.

    :param tango_control_handle: instance of Tango control class
    """
    ipath = "resources"
    _module_logger.info("Read input files in %s", ipath)
    rv = tango_control_handle.read_input_files(ipath, True)
    assert rv == 0


def test_namespaces_dict(kube_namespace: str, tango_control_handle: Any) -> None:
    """
    Test K8S namespaces.

    :param kube_namespace: K8S namespace
    :param tango_control_handle: instance of Tango control class
    """
    _module_logger.info("Read namespaces")
    k8s_namespaces_dict = tango_control_handle.get_namespaces_dict()
    assert len(k8s_namespaces_dict) > 0


def test_namespaces_list(tango_control_handle: Any) -> None:
    """
    Test K8S namespaces.

    :param tango_control_handle: instance of Tango control class
    """
    _module_logger.info("List namespaces")
    k8s_namespaces_list = tango_control_handle.get_namespaces_list()
    assert len(k8s_namespaces_list) > 0


def test_pods_dict(kube_namespace: str, tango_control_handle: Any) -> None:
    """
    Test for reading pods.

    :param kube_namespace: K8S namespace
    :param tango_control_handle: instance of Tango control class
    """
    _module_logger.info("Read pods")
    k8s_pods_dict = tango_control_handle.get_pods_dict(kube_namespace)
    assert len(k8s_pods_dict) > 0


def test_basic_devices(configuration_data: dict) -> None:
    """
    Read basic devices.

    :param configuration_data: read from JSON file
    """
    _module_logger.info("List device classes")
    devices = TangoctlDevicesBasic(_module_logger, True, False, configuration_data, None, "json")

    devices.read_config()
    devdict = devices.make_json()
    assert len(devdict) > 0


def test_device_read(configuration_data: dict, device_name: str) -> None:
    """
    Read devices.

    :param configuration_data: read from JSON file
    :param device_name: Tango device
    """
    devices = TangoctlDevices(
        _module_logger,
        True,
        False,
        configuration_data,
        device_name,
        None,
        None,
        None,
        0,
        None,
        "json",
    )
    devices.read_device_values()
    devdict = devices.make_json()
    assert len(devdict) > 0
