#!/usr/bin/python
"""
Read information about Tango devices.
"""
import getopt
import json
import logging
import os
import sys
from typing import Any, TextIO

from ska_mid_itf_engineering_tools.k8s_info.get_k8s_info import KubernetesControl
from ska_mid_itf_engineering_tools.ska_jargon.ska_jargon import print_jargon
from ska_mid_itf_engineering_tools.tango_info.get_tango_info import (
    check_tango,
    show_attributes,
    show_command_inputs,
    show_commands,
    show_devices,
    show_properties,
)

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
    print(f"Namespaces : {len(ns_list)}")
    for ns_name in ns_list:
        print(f"\t{ns_name}")


def usage(p_name: str, cfg_data: Any) -> None:
    """
    Show how it is done.

    :param p_name: executable name
    :param cfg_data: configuration in JSON format
    """
    print("Display Kubernetes namespaces")
    print(f"\t{p_name} -n")
    print("Display Tango database address")
    print(f"\t{p_name} -t [--namespace=<NAMESPACE>|--host=<HOST>]")
    print(f"\t{p_name} -t [-N <NAMESPACE>|-H <HOST>]")
    print("Display Tango device names")
    print(f"\t{p_name} -d [--namespace=<NAMESPACE>|--host=<HOST>]")
    print(f"\t{p_name} -d [-N <NAMESPACE>|-H <HOST>]")
    print("Display all devices")
    print(f"\t{p_name} -f|-l|-q|-s [--dry-run] [--namespace=<NAMESPACE>|--host=<HOST>]")
    print(f"\t{p_name} -f|-l|-q|-s [-N <NAMESPACE>|-H <HOST>]")
    print("Filter on device name")
    print(f"\t{p_name} -f|-l|-q|-s -D <DEVICE> [-N <NAMESPACE>|-H <HOST>]")
    print(
        f"\t{p_name} -f|-l|-q|-s --device=<DEVICE>"
        " [--namespace=<NAMESPACE>|--host=<HOST>]"
    )
    print("Filter on attribute name")
    print(
        f"\t{p_name} -f|-l|-q|-s --attribute=<ATTRIBUTE>"
        " [--namespace=<NAMESPACE>|--host=<HOST>]"
    )
    print(f"\t{p_name} -f|-l|-q|-s -A <ATTRIBUTE> [-N <NAMESPACE>|-H <HOST>]")
    print("Filter on command name")
    print(
        f"\t{p_name} -f|-l|-q|-s --command=<COMMAND>"
        " [--namespace=<NAMESPACE>|--host=<HOST>]"
    )
    print(f"\t{p_name} -f|-l|-q|-s -C <COMMAND> [-N <NAMESPACE>|-H <HOST>]")
    print("Filter on property name")
    print(
        f"\t{p_name} -f|-l|-q|-s --property=<PROPERTY>"
        " [--namespace=<NAMESPACE>|--host=<HOST>]"
    )
    print(
        f"\t{p_name} -f|-l|-q|-s -P <PROPERTY>"
        " [-N <NAMESPACE>|--host=<HOST>]"
    )
    print("Display known acronyms")
    print(f"\t{p_name} -j")
    print("where:")
    print("\t-f\t\t\t\tdisplay in full")
    print("\t-l\t\t\t\tdisplay device name and status on one line")
    print("\t-q\t\t\t\tdisplay device name, status and query devices")
    print("\t-s\t\t\t\tdisplay device name and status only")
    # print("\t-m\t\t\t\tdisplay in markdown format")
    print("\t-f\t\t\t\tget commands, attributes and properties regardless of state")
    print(
        "\t--device=<DEVICE>\t\tdevice name, e.g. 'csp'"
        " (not case sensitive, only a part is needed)"
    )
    print(
        "\t--namespace=<NAMESPACE>\t\tKubernetes namespace for Tango database,"
        " e.g. 'integration'"
    )
    print("\t--host=<HOST>\t\t\tTango database host and port, e.g. 10.8.13.15:10000")
    print(
        "\t--attribute=<ATTRIBUTE>\t\tattribute name, e.g. 'obsState' (case sensitive)"
    )
    print("\t--command=<COMMAND>\t\tcommand name, e.g. 'Status' (case sensitive)")

    print(
        "\t-D <DEVICE>\t\t\tdevice name, e.g. 'csp'"
        " (not case sensitive, only a part is needed)"
    )
    print(
        "\t-N <NAMESPACE>\t\t\tKubernetes namespace for Tango database,"
        f" default is {KUBE_NAMESPACE}"
    )
    print("\t-H <HOST>\t\t\tTango database host and port, e.g. 10.8.13.15:10000")
    print("\t-A <ATTRIBUTE>\t\t\tattribute name, e.g. 'obsState' (case sensitive)")
    print("\t-C <COMMAND>\t\t\tcommand name, e.g. 'Status' (case sensitive)")
    # print(f"Run commands : {','.join(cfg_data['run_commands'])}")
    # print(f"Run commands with name : {','.join(cfg_data['run_commands_name'])}")


def main(y_arg: list) -> int:  # noqa: C901
    """
    Read and display Tango devices.

    :param y_arg: input arguments
    :return: error condition
    """
    global KUBE_NAMESPACE

    dry_run: bool = False
    itype: str | None = None
    disp_action: int = 0
    evrythng: bool = False
    show_jargon: bool = False
    show_ns: bool = False
    show_tango: bool = False
    tgo_attrib: str | None = None
    tgo_cmd: str | None = None
    tgo_in_type: str | None = None
    tgo_prop: str | None = None
    tango_host: str | None = None
    try:
        opts, _args = getopt.getopt(
            y_arg[1:],
            "defhjlmnqstvVA:C:H:D:N:P:T:",
            [
                "dry-run",
                "help",
                "input",
                "host=",
                "device=",
                "attribute=",
                "command=",
                "namespace=",
                "property=",
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
        elif opt in ("-A", "--attribute"):
            tgo_attrib = arg
        elif opt in ("-C", "--command"):
            tgo_cmd = arg
        elif opt in ("-H", "--host"):
            tango_host = arg
        elif opt in ("-D", "--device"):
            itype = arg.upper()
        elif opt in ("-N", "--namespace"):
            KUBE_NAMESPACE = arg
        elif opt in ("-P", "--property"):
            tgo_prop = arg
        elif opt in ("-T", "--input"):
            tgo_in_type = arg.lower()
        elif opt == "--dry-run":
            dry_run = True
        elif opt == "-j":
            show_jargon = True
        elif opt == "-t":
            show_tango = True
        elif opt == "-m":
            disp_action = 2
        elif opt == "-f":
            disp_action = 1
        elif opt == "-e":
            evrythng = True
        elif opt == "-n":
            show_ns = True
        elif opt == "-q":
            disp_action = 3
        elif opt == "-d":
            disp_action = 4
        elif opt == "-s":
            disp_action = 5
        elif opt == "-l":
            disp_action = 6
        elif opt == "-v":
            _module_logger.setLevel(logging.INFO)
        elif opt == "-V":
            _module_logger.setLevel(logging.DEBUG)
        else:
            _module_logger.error("Invalid option %s", opt)

    if show_jargon:
        print_jargon()
        return 0

    if show_ns:
        show_namespaces()
        return 0

    if tango_host is None:
        tango_fqdn = f"{DATABASEDS_NAME}.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}"
        tango_host = f"{tango_fqdn}:10000"
    else:
        tango_fqdn = tango_host.split(":")[0]

    if show_tango:
        check_tango(tango_fqdn)
        return 0

    os.environ["TANGO_HOST"] = tango_host
    _module_logger.info("Set TANGO_HOST to %s", tango_host)

    if tgo_attrib is not None:
        show_attributes(_module_logger, disp_action, evrythng, tgo_attrib)
        return 0

    if tgo_cmd is not None:
        show_commands(_module_logger, disp_action, evrythng, tgo_cmd)
        return 0

    if tgo_in_type is not None:
        show_command_inputs(_module_logger, tango_host, tgo_in_type)
        return 0

    if tgo_prop is not None:
        show_properties(_module_logger, disp_action, evrythng, tgo_prop)
        return 0

    if not disp_action:
        print("Nothing to do!")
        return 1

    show_devices(_module_logger, cfg_data, disp_action, evrythng, itype, dry_run)

    return 0


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
