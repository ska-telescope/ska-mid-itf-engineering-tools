#!/usr/bin/python
"""Read all information about Tango devices."""

import getopt
import json
import logging
import os
import sys
from typing import Any, TextIO

from ska_mid_itf_engineering_tools import __version__
from ska_mid_itf_engineering_tools.k8s_info.get_k8s_info import KubernetesControl
from ska_mid_itf_engineering_tools.ska_jargon.ska_jargon import print_jargon
from ska_mid_itf_engineering_tools.tango_info.get_tango_attributes import show_attributes
from ska_mid_itf_engineering_tools.tango_info.get_tango_commands import show_commands
from ska_mid_itf_engineering_tools.tango_info.get_tango_devices import show_devices
from ska_mid_itf_engineering_tools.tango_info.get_tango_info import (
    check_tango,
    show_command_inputs,
)
from ska_mid_itf_engineering_tools.tango_info.get_tango_properties import show_properties

logging.basicConfig(level=logging.WARNING)
_module_logger = logging.getLogger(__name__)
_module_logger.setLevel(logging.WARNING)


def show_namespaces() -> None:
    """Display namespace in Kubernetes cluster."""
    k8s = KubernetesControl(_module_logger)
    ns_list = k8s.get_namespaces_list()
    print(f"Namespaces : {len(ns_list)}")
    for ns_name in ns_list:
        print(f"\t{ns_name}")


def usage(p_name: str, cfg_data: Any) -> None:
    """
    Show how it is done.

    :param p_name: executable name
    :param cfg_data: configuration in JSON format
    """
    print("Read Tango devices.")
    print("Display version number:")
    print(f"\t{p_name} --version")
    print("Display help")
    print(f"\t{p_name} --help")
    print(f"\t{p_name} -h")
    print("Display Kubernetes namespaces:")
    print(f"\t{p_name} --show-ns")
    print(f"\t{p_name} -n")
    print("Display Tango database address:")
    print(f"\t{p_name} --show-db [--k8s-ns=<NAMESPACE>|--host=<HOST>]")
    print(f"\t{p_name} -t [-K <NAMESPACE>|-H <HOST>]")
    print("Display Tango device names:")
    print(f"\t{p_name} --show-dev [--k8s-ns=<NAMESPACE>|--host=<HOST>]")
    print(f"\t{p_name} -d [-K <NAMESPACE>|-H <HOST>]")
    print("Display all devices:")
    print(
        f"\t{p_name} --full|--list|--quick|--short [--dry-run]"
        f" [--k8s-ns=<NAMESPACE>|--host=<HOST>]"
    )
    print(f"\t{p_name} -f|-l|-q|-s [-K <NAMESPACE>|-H <HOST>]")
    print("Filter on device name:")
    print(f"\t{p_name} --full|--list|--quick|--short -D <DEVICE> [-K <NAMESPACE>|-H <HOST>]")
    print(f"\t{p_name} -f|-l|-q|-s --device=<DEVICE> [--k8s-ns=<NAMESPACE>|--host=<HOST>]")
    print("Filter on attribute name:")
    print(
        f"\t{p_name} --full|--list|--quick|--short --attribute=<ATTRIBUTE>"
        " [--k8s-ns=<NAMESPACE>|--host=<HOST>]"
    )
    print(f"\t{p_name} -f|-l|-q|-s -A <ATTRIBUTE> [-K <NAMESPACE>|-H <HOST>]")
    print("Filter on command name:")
    print(
        f"\t{p_name} --full|--list|--quick|--short --command=<COMMAND>"
        " [--k8s-ns=<NAMESPACE>|--host=<HOST>]"
    )
    print(f"\t{p_name} -f|-l|-q|-s -C <COMMAND> [-K <NAMESPACE>|-H <HOST>]")
    print("Filter on property name:")
    print(
        f"\t{p_name} --full|--list|--quick|--short --property=<PROPERTY>"
        " [--k8s-ns=<NAMESPACE>|--host=<HOST>]"
    )
    print(f"\t{p_name} -f|-l|-q|-s -P <PROPERTY> [-K <NAMESPACE>|--host=<HOST>]")
    print("Display known acronyms:")
    print(f"\t{p_name} -j")
    print("where:")
    print("\t-f|--full\t\t\tdisplay in full")
    print("\t-l|--list\t\t\tdisplay device name and status on one line")
    print("\t-q|--quick\t\t\tdisplay device name, status and query devices")
    print("\t-s|--short\t\t\tdisplay device name and status only")
    # print("\t-m\t\t\t\tdisplay in markdown format")
    print("\t-f\t\t\t\tget commands, attributes and properties regardless of state")
    print(
        "\t--device=<DEVICE>\t\tdevice name, e.g. 'csp'"
        " (not case sensitive, only a part is needed)"
    )
    print("\t--k8s-ns=<NAMESPACE>\t\tKubernetes namespace for Tango database, e.g. 'integration'")
    print("\t--host=<HOST>\t\t\tTango database host and port, e.g. 10.8.13.15:10000")
    print("\t--attribute=<ATTRIBUTE>\t\tattribute name, e.g. 'obsState' (not case sensitive)")
    print("\t--command=<COMMAND>\t\tcommand name, e.g. 'Status' (not case sensitive)")
    print("\t-D <DEVICE>\t\t\tdevice name, e.g. 'csp' (not case sensitive, only a part is needed)")
    print("\t-K <NAMESPACE>\t\t\tKubernetes namespace for Tango database")
    print("\t-H <HOST>\t\t\tTango database host and port, e.g. 10.8.13.15:10000")
    print("\t-A <ATTRIBUTE>\t\t\tattribute name, e.g. 'obsState' (not case sensitive)")
    print("\t-C <COMMAND>\t\t\tcommand name, e.g. 'Status' (not case sensitive)")
    print("Note that values for device, attribute, command or property are not case sensitive.")
    print(f"Partial matches for strings longer than {cfg_data['min_str_len']} charaters are OK.")
    print("When a namespace is specified, the Tango database host will be made up as follows:")
    print(
        f"\t{cfg_data['databaseds_name']}.<NAMESPACE>.{cfg_data['cluster_domain']}"
        f":{cfg_data['databaseds_port']}"
    )
    # print(f"Run commands : {','.join(cfg_data['run_commands'])}")
    # print(f"Run commands with name : {','.join(cfg_data['run_commands_name'])}")


def main(y_arg: list) -> int:  # noqa: C901
    """
    Read and display Tango devices.

    :param y_arg: input arguments
    :return: error condition
    """
    kube_namespace: str | None = None
    dry_run: bool = False
    itype: str | None = None
    disp_action: int = 0
    evrythng: bool = False
    headers = True
    show_jargon: bool = False
    show_ns: bool = False
    show_tango: bool = False
    show_version: bool = False
    tgo_attrib: str | None = None
    tgo_cmd: str | None = None
    tgo_in_type: str | None = None
    tgo_prop: str | None = None
    tango_host: str | None = None
    fmt: str = "txt"
    try:
        opts, _args = getopt.getopt(
            y_arg[1:],
            "efhjlmkqstvVA:C:H:D:K:P:T:",
            [
                "dry-run",
                "everything",
                "full",
                "help",
                "list",
                "no-headers",
                "input",
                "quick",
                "short",
                "show-acronym",
                "show-db",
                "show-dev",
                "show-ns",
                "version",
                "attribute=",
                "command=",
                "device=",
                "host=",
                "k8s-ns=",
                "property=",
            ],
        )
    except getopt.GetoptError as opt_err:
        print(f"Could not read command line: {opt_err}")
        return 1

    # Read configuration file
    cfg_name: str | bytes = y_arg[0] + ".json"
    cfg_file: TextIO = open(cfg_name)
    cfg_data: Any = json.load(cfg_file)
    cfg_file.close()
    databaseds_name: str = cfg_data["databaseds_name"]
    cluster_domain: str = cfg_data["cluster_domain"]
    min_str_len: int = cfg_data["min_str_len"]
    databaseds_port: int = cfg_data["databaseds_port"]

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(os.path.basename(y_arg[0]), cfg_data)
            sys.exit(1)
        elif opt == "--version":
            show_version = True
        elif opt in ("-A", "--attribute"):
            tgo_attrib = arg
        elif opt in ("-C", "--command"):
            tgo_cmd = arg
        elif opt in ("-D", "--device"):
            itype = arg.upper()
        elif opt in ("-H", "--host"):
            tango_host = arg
        elif opt in ("-T", "--input"):
            # Undocumented feature to search by input type
            tgo_in_type = arg.lower()
        elif opt in ("-K", "--k8s-ns"):
            kube_namespace = arg
        elif opt in ("-P", "--property"):
            tgo_prop = arg
        elif opt == "--dry-run":
            # Undocumented feature for dry runs
            dry_run = True
        elif opt == "--no-headers":
            headers = False
        # elif opt in ("-d", "--show-dev"):
        #     disp_action = 4
        elif opt in ("-e", "--everything"):
            evrythng = True
        elif opt in ("-f", "--full"):
            disp_action = 1
        elif opt in ("-l", "--list"):
            disp_action = 4
        elif opt == "-m":
            # Undocumented feature to display in mark-down format
            fmt = "md"
        elif opt in ("-k", "--show-ns"):
            show_ns = True
        elif opt in ("-q", "--quick"):
            disp_action = 3
        elif opt in ("-j", "--show-acronym"):
            show_jargon = True
        elif opt in ("-s", "--short"):
            disp_action = 5
        elif opt in ("-t", "--show-db"):
            show_tango = True
        elif opt == "-v":
            _module_logger.setLevel(logging.INFO)
        elif opt == "-V":
            _module_logger.setLevel(logging.DEBUG)
        else:
            _module_logger.error("Invalid option %s", opt)

    if show_version:
        print(f"{os.path.basename(y_arg[0])} version {__version__}")
        return 0

    if show_jargon:
        print_jargon()
        return 0

    if show_ns:
        show_namespaces()
        return 0

    if kube_namespace is None and tango_host is None:
        tango_host = os.getenv("TANGO_HOST")
        if tango_host is None:
            print("No Kubernetes namespace or Tango database server specified, TANGO_HOST not set")
            return 1

    if tango_host is None:
        tango_fqdn = f"{databaseds_name}.{kube_namespace}.svc.{cluster_domain}"
        tango_host = f"{tango_fqdn}:{databaseds_port}"
    elif ":" in tango_host:
        tango_fqdn = tango_host.split(":")[0]
    else:
        tango_fqdn = tango_host
        tango_host = f"{tango_fqdn}:{databaseds_port}"

    if show_tango:
        check_tango(tango_fqdn)
        return 0

    _module_logger.info("Use Tango host %s", tango_host)

    _module_logger.debug("Run commands: %s", cfg_data["run_commands_name"])
    _module_logger.debug("Run commands with name: %s", cfg_data["run_commands"])

    os.environ["TANGO_HOST"] = tango_host
    _module_logger.info("Set TANGO_HOST to %s", tango_host)

    if tgo_attrib is not None:
        show_attributes(_module_logger, cfg_data, disp_action, evrythng, tgo_attrib, dry_run, fmt)
        return 0

    if tgo_cmd is not None:
        show_commands(_module_logger, cfg_data, disp_action, evrythng, tgo_cmd, dry_run, fmt)
        return 0

    if tgo_in_type is not None:
        show_command_inputs(_module_logger, tango_host, tgo_in_type, min_str_len)
        return 0

    if tgo_prop is not None:
        show_properties(_module_logger, cfg_data, disp_action, evrythng, tgo_prop, dry_run, fmt)
        return 0

    if not disp_action:
        print("Nothing to do!")
        return 1

    show_devices(_module_logger, cfg_data, disp_action, evrythng, itype, headers, dry_run, fmt)

    return 0


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
