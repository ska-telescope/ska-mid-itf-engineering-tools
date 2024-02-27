#!/usr/bin/python
"""
Test devices from Tango database.
"""
import getopt
import json
import logging
import os
import sys
from typing import Any, TextIO

from ska_mid_itf_engineering_tools.k8s_info.get_k8s_info import KubernetesControl
from ska_mid_itf_engineering_tools.tango_info.test_tango_device import TestTangoDevice

logging.basicConfig(level=logging.WARNING)
_module_logger = logging.getLogger(__name__)
_module_logger.setLevel(logging.WARNING)

KUBE_NAMESPACE = "ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2"
CLUSTER_DOMAIN = "miditf.internal.skao.int"
DATABASEDS_NAME = "tango-databaseds"


def show_namespaces() -> None:
    """
    Display namespace in Kubernetes cluster.
    """
    k8s = KubernetesControl(_module_logger)
    ns_list = k8s.get_namespaces()
    print(f"[  OK  ] Namespaces : {len(ns_list)}")
    for ns_name in ns_list:
        print(f"\t{ns_name}")


def check_namespace(kube_namespace: str) -> int:
    """
    Display namespace in Kubernetes cluster.
    :param kube_namespace: Kubernetes namespace
    :return: error condition
    """
    k8s = KubernetesControl(_module_logger)
    ns_list = k8s.get_namespaces()
    print(f"[  OK  ] Namespaces : {len(ns_list)}")
    if kube_namespace in ns_list:
        print(f"[  OK  ] namespace {kube_namespace} is valid")
        return 0
    print(f"[  OK  ] namespace {kube_namespace} is not valid")
    return 1


def usage(p_name: str, cfg_data: Any) -> None:
    """
    Show how it is done.

    :param p_name: executable name
    """
    print("Test a Tango device")
    print(f"\t{p_name} [-N <NAMESPACE>] -D <DEVICE> [--simul=<0|1>]")
    print("Test a Tango device and read attributes")
    print(f"\t{p_name} -a [-N <NAMESPACE>] -D <DEVICE> [--simul=<0|1>]")
    print("Display attribute and command names for a Tango device")
    print(f"\t{p_name} -c [-N <NAMESPACE>] -D <DEVICE>")
    print("Turn a Tango device on")
    print(f"\t{p_name} --on [-N <NAMESPACE>] -D <DEVICE> [--simul=<0|1>]")
    print("Turn a Tango device off")
    print(f"\t{p_name} --off [-N <NAMESPACE>] -D <DEVICE> [--simul=<0|1>]")
    print("Set a Tango device to standby mode")
    print(f"\t{p_name} --standby [-N <NAMESPACE>] -D <DEVICE> [--simul=<0|1>]")
    print("Change admin mode on a Tango device")
    print(f"\t{p_name} --admin=<0|1>")
    print("Display status of a Tango device")
    print(f"\t{p_name} --status [-N <NAMESPACE>] -D <DEVICE>")
    print("Check events for attribute of a Tango device")
    print(f"\t{p_name} [-N <NAMESPACE>] -D <DEVICE> -A <ATTRIBUTE>")
    print("where:")
    print(
        "\t-D <DEVICE>\t\tdevice name, e.g. 'csp'"
        " (not case sensitive, only a part is needed)"
    )
    print(
        "\t-N <NAMESPACE>\t\tKubernetes namespace for Tango database,"
        f" default is '{KUBE_NAMESPACE}'"
    )
    print("\t-a\t\t\tflag for reading attributes")
    print("\t-c\t\t\tflag for reading command and attribute names")
    print("\t--simul=<0|1>\t\tset simulation mode off or on")
    print("\t--admin=<0|1>\t\tset admin mode off or on")
    print("\t-N <NAMESPACE\t\tKubernetes namespace")
    print("\t-D <DEVICE>\t\tTango device triplet")
    print("\t-A <ATTRIBUTE>\t\tTango device attribute name")


def main(y_arg: list) -> int:  # noqa: C901
    """
    Read and display Tango devices.

    :param y_arg: input arguments
    :return: error condition
    """
    global KUBE_NAMESPACE
    dev_name: str | None = None
    show_ns: bool = False
    tgo_attrib: str | None = None
    tango_host: str | None = None
    show_attrib: bool = False
    show_command: bool = False
    dev_on: bool = False
    dev_off: bool = False
    dev_standby: bool = False
    dev_status: bool = False
    dev_admin: int | None = None
    dev_sim: int | None = None
    dev_nodb: bool = False
    run_test: bool = False
    try:
        opts, _args = getopt.getopt(
            y_arg[1:],
            "acghnvVA:H:D:N:",
            [
                "help",
                "nodb",
                "off",
                "on",
                "standby",
                "status",
                "test",
                "host=",
                "admin=",
                "device=",
                "attribute=",
                "namespace=",
                "simul=",
            ],
        )
    except getopt.GetoptError as opt_err:
        print(f"Could not read command line: {opt_err}")
        return 1

    cfg_name: str | bytes = os.path.basename(y_arg[0]).replace(".py", ".json")
    cfg_read: str = os.path.dirname(y_arg[0]) + "/" + cfg_name
    cfg_file: TextIO = open(cfg_read)
    cfg_data: Any = json.load(cfg_file)
    cfg_file.close()

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(os.path.basename(y_arg[0]), cfg_data)
            sys.exit(1)
        elif opt == "--admin":
            dev_admin = int(arg)
        elif opt in ("-A", "--attribute"):
            tgo_attrib = arg
        elif opt in ("-H", "--host"):
            tango_host = arg
        elif opt in ("-D", "--device"):
            dev_name = arg
        elif opt in ("-N", "--namespace"):
            KUBE_NAMESPACE = arg
        elif opt == "-a":
            show_attrib = True
        elif opt == "-c":
            show_command = True
        elif opt == "-n":
            show_ns = True
        elif opt == "--nodb":
            dev_nodb = True
        elif opt == "--off":
            dev_off = True
        elif opt == "--on":
            dev_on = True
        elif opt == "--simul":
            dev_sim = int(arg)
        elif opt == "--standby":
            dev_standby = True
        elif opt == "--status":
            dev_status = True
        elif opt == "-v":
            _module_logger.setLevel(logging.INFO)
        elif opt == "-V":
            _module_logger.setLevel(logging.DEBUG)
        else:
            _module_logger.error("Invalid option %s", opt)
            return 1

    if show_ns:
        show_namespaces()
        return 0

    if dev_nodb:
        if tango_host is not None:
            dev_name = f"tango://{tango_host}/{dev_name}#dbase=no"
        else:
            dev_name = f"tango://127.0.0.1:45450/{dev_name}#dbase=no"
    elif tango_host is None:
        tango_fqdn = f"{DATABASEDS_NAME}.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}"
        tango_host = f"{tango_fqdn}:10000"
    else:
        tango_fqdn = tango_host.split(":")[0]

    # if show_tango:
    #     check_tango(tango_fqdn)
    #     return 0

    os.environ["TANGO_HOST"] = tango_host
    _module_logger.info("Set TANGO_HOST to %s", tango_host)

    print(f"[  OK  ] Namespace set to {KUBE_NAMESPACE}")
    rc = check_namespace(KUBE_NAMESPACE)
    if rc:
        return 1

    if dev_admin is not None and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        dut.test_admin_mode(dev_admin)
    elif dev_off and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_off(dev_sim)
    elif dev_on and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_on(dev_sim)
    elif dev_standby and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_standby(dev_sim)
    elif dev_status and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_status()
    elif dev_sim is not None and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_simulation_mode(dev_sim)
    # elif show_attrib and dev_name is not None:
    #     dut = TestTangoDevice(_module_logger, dev_name)
    #     if dut.dev is None:
    #         print(f"[FAILED] could not open device {dev_name}")
    #         return 1
    #     dut.check_device()
    #     dut.get_simulation_mode()
    #     dut.show_device_attributes(True)
    elif show_command and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.check_device()
        # dut.get_simulation_mode()
        dut.show_device_attributes(True)
        dut.show_device_commands(True)
    elif tgo_attrib is not None and dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_subscribe(tgo_attrib)
    elif dev_name is not None:
        dut = TestTangoDevice(_module_logger, dev_name)
        if dut.dev is None:
            print(f"[FAILED] could not open device {dev_name}")
            return 1
        dut.test_all(show_attrib)
    else:
        # List available devices
        # devices = get_devices()
        # print(f"[  OK  ] Devices: {len(devices)}")
        # for device in devices:
        #     print(f"\t{device}")
        print("Nothing to do!")

    return 0


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
