"""
Unit tests for tangoctl.

# type: ignore[import-untyped]
"""

import json
import logging
from typing import Any, TextIO

import pytest

from ska_mid_itf_engineering_tools.tango_control.tango_control import (
    get_namespaces_dict,
    get_namespaces_list,
    get_pods_dict,
)

KUBE_NAMESPACE: str = "integration"
DEVICE_NAME = "mid-csp/capability-fsp/0"

logging.basicConfig(level=logging.WARNING)
_module_logger = logging.getLogger("conftest")
_module_logger.setLevel(logging.WARNING)


@pytest.fixture(name="kube_namespace")
def kube_namespace() -> str:
    """
    Get K8S namespace.

    :return: K8S namespace
    """
    return KUBE_NAMESPACE


@pytest.fixture(name="device_name")
def device_name() -> str:
    """
    Get Tango device name.

    :return: Tango device name
    """
    return DEVICE_NAME


@pytest.fixture(name="configuration_data")
def configuration_data() -> dict:
    """
    Read configuration file.

    :return: dictionary read from configuration file
    """
    cfg_name: str | bytes = "src/ska_mid_itf_engineering_tools/tango_control/tangoctl.json"
    cfg_file: TextIO = open(cfg_name)
    cfg_data: Any = json.load(cfg_file)
    cfg_file.close()
    return cfg_data


@pytest.fixture(name="k8s_namespaces_dict")
def k8s_namespaces_dict() -> dict:
    """
    Get namespaces in JSON format.

    :return: dictionary with data read from Kubernetes
    """
    ns_dict = get_namespaces_dict()
    return ns_dict


@pytest.fixture(name="k8s_namespaces_list")
def k8s_namespaces_list() -> list:
    """
    Get namespaces in JSON format.

    :return: list with data read from Kubernetes
    """
    ns_list = get_namespaces_list()
    return ns_list


@pytest.fixture(name="k8s_pods_dict")
def k8s_pods_dict() -> dict:
    """
    Get pods in JSON formant.

    :return: dictionary with data read from Kubernetes
    """
    pods_dict = get_pods_dict(KUBE_NAMESPACE)
    return pods_dict
