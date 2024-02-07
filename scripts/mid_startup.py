#!/usr/bin/python
"""
Start and stop Central Signal Processor (CSP) or Telescope Monitor and Control (TMC).

Use to test functionality used in notebooks.

CSP assign resources:
https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/ska-csp-assignresources.html
CSP configure:
https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/ska-csp-configure.html
CSP scan:
https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/ska-csp-scan.html
CSP end scan:
https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/ska-csp-endscan.html
CSP release resources:
https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/ska-csp-releaseresources.html
CSP delay model:
https://developer.skao.int/projects/ska-telmodel/en/latest/schemas/ska-csp-delaymodel.html
"""
import getopt
import logging
import os
import sys
from typing import Any, List, Tuple

import ska_ser_logging  # type: ignore[import]

from ska_mid_itf.tango_info.get_tango_info import (
    check_tango,
    show_long_running_commands,
)
from ska_mid_itf.ska_notebook_helper.mid_itf_control import (
    do_control,
    do_shutdown,
    do_startup,
    read_config_file,
    show_config_json,
    show_observation_status,
)

from ska_mid_itf.ska_jargon.ska_jargon import get_ska_jargon

ska_ser_logging.configure_logging(logging.DEBUG)
_module_logger: logging.Logger = logging.getLogger(__name__)

# LONG_RUN_CMDS: int = 4
#
# LEAFNODE_DEVICE = "ska_mid/tm_leaf_node/csp_subarray_01"
# BITE_POD = "ec-bite"
# BITE_CMD = ["python3", "midcbf_bite.py", "--talon-bite-lstv-replay", "--boards=1"]
# TIMEOUT = 60





def usage(p_name: str, mid_sys: str, cfg_data: Any) -> None:
    """
    Show how it is done.

    :param p_name: executable name
    :param mid_sys: subsystem name
    :param cfg_data: configuration data
    """
    print("Start system:")
    print(
        f"\t{p_name} --start"
        " [--csp|--tmc] [--simul]"
        " [--jobs=<JOBS>]"
        " [--csp|--tmc]"
        " [--control=<DEVICE>]"
        " [--subarray=<DEVICE]"
        " [--leafnode=<LEAFNODE>]"
        " [--namespace=<NAMESPACE>]"
        " [--service=<SERVICE>]"
        " [--system=<SYSTEM>]"
    )
    print("Control system:")
    print(
        f"\t{p_name} --ctrl"
        " [--csp|--tmc]"
        " [--subarray=<DEVICE]"
        " [--namespace=<NAMESPACE>]"
        " [--leafnode=<LEAFNODE>]"
    )
    print("Stop system:")
    print(
        f"\t{p_name} --stop [--teardown]"
        " [--csp|--tmc]"
        " [--control=<DEVICE>]"
        " [--subarray=<DEVICE]"
    )
    print("Check Tango status:")
    print(f"\t{p_name} -t")
    print("Display observation state:")
    print(f"\t{p_name} --observation [--subarray=<DEVICE]")
    print("Display long running commands:")
    print(f"\t{p_name} --long-cmd [--subarray=<DEVICE]")
    print("where:")
    for mid_sys in ("csp", "tmc"):
        print(
            f"\t--{mid_sys}\tuse {get_ska_jargon(mid_sys)} subsystem:"
        )
        if mid_sys in ["csp"]:
            print(
                "\t\t--jobs=<JOBS>\t\tMinimum number of long running commands,"
                f" default for {mid_sys.upper()}"
                f" is {cfg_data[mid_sys]['long_run_cmds']}"
            )
        print(
            "\t\t--control=<DEVICE>\tTango control device,"
            f"default for {mid_sys.upper()} is {cfg_data[mid_sys]['control_device']}"
        )
        print(
            "\t\t--subarray=<DEVICE>\tTango subarray device,"
            f"default for {mid_sys.upper()} is {cfg_data[mid_sys]['subarray_device']}"
        )
        print(
            "\t\t--leafnode=<LEAFNODE>\tTango leafnode device,"
            f" default for {mid_sys.upper()} is {cfg_data[mid_sys]['leafnode_device']}"
        )
    print(f"\t--simul\t\t\tsimulate {get_ska_jargon('CBF')}")
    print(
        "\t--namespace=<NAMESPACE>\tKubernetes namespace,"
        f" default is {cfg_data['kube_namespace']}"
    )
    print(
        "\t--service=<SERVICE>\tKubernetes service for Tango database,"
        f" default is {cfg_data['databaseds_name']}"
    )
    print("\t--teardown\t\tTear down control device at the end")


def main(y_arg: list) -> int:  # noqa: C901
    """
    Start Tango devices for MID ITF.

    :param y_arg: input arguments
    """
    cfg_data = read_config_file(f"{os.path.dirname(y_arg[0])}/mid_startup.json")

    ns_name: str = cfg_data["kube_namespace"]
    svc_name: str = cfg_data["databaseds_name"]
    cluster_domain: str = cfg_data["cluster_domain"]
    databaseds_name: str = cfg_data["databaseds_name"]
    timeout = cfg_data["timeout"]
    mid_sys = ""
    sub_dev: Any = None
    ctl_dev_name: str = ""
    sub_dev_name: str = ""
    leaf_dev_name: str = ""
    resource_data: str = ""
    long_cmds: int = -1
    bite_cmd: List[str] = []
    # TODO read JSON data from file
    _resource_file: str | None = None  # noqa: F841
    show_tango: bool = False
    show_status: bool = False
    tear_down = False
    show_cfg = False
    show_obs = False
    show_long = False
    dev_start = False
    dev_ctrl = False
    dev_stop = False
    dev_sim = False

    try:
        opts, _args = getopt.getopt(
            y_arg[1:],
            "acdefhlopstvVC:D:J:L:N:R:S:",
            [
                "help",
                "csp",
                "tmc",
                "config",
                "long-cmd",
                "observation",
                "sim",
                "start",
                "ctrl",
                "stop",
                "teardown",
                "status",
                "jobs=",
                "namespace=",
                "service=",
                "control=",
                "subarray=",
                "leafnode=",
                "resource=",
            ],
        )  # noqa: F841
    except getopt.GetoptError as opt_err:
        print(f"Could not read command line: {opt_err}")
        return 1

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(os.path.basename(y_arg[0]), mid_sys, cfg_data)
            sys.exit(1)
        elif opt in ("-C", "--control"):
            ctl_dev_name = arg
        elif opt in ("-D", "--subarray"):
            sub_dev_name = arg
        elif opt in ("-J", "--jobs"):
            long_cmds = int(arg)
        elif opt in ("-L", "--leafnode"):
            leaf_dev_name = arg
        elif opt in ("-N", "--namespace"):
            ns_name = arg
        elif opt in ("-S", "--service"):
            svc_name = arg
        elif opt in ("-c", "--config"):
            show_cfg = True
        elif opt == "--sim":
            dev_sim = True
        elif opt == "--start":
            dev_start = True
        elif opt == "--ctrl":
            dev_ctrl = True
        elif opt == "--stop":
            dev_stop = True
        elif opt in ("-d", "--teardown"):
            tear_down = True
        elif opt in ("-a", "--status"):
            show_status = True
        elif opt in ("-l", "--long-cmd"):
            show_long = True
        elif opt in ("-o", "--observation"):
            show_obs = True
        elif opt == "--csp":
            mid_sys = "csp"
        elif opt == "--tmc":
            mid_sys = "tmc"
        elif opt == "-t":
            show_tango = True
        elif opt == "-v":
            ska_ser_logging.configure_logging(logging.INFO)
            _module_logger.setLevel(logging.INFO)
        elif opt == "-V":
            ska_ser_logging.configure_logging(logging.DEBUG)
            _module_logger.setLevel(logging.DEBUG)
        else:
            print("Invalid option %s" % opt)

    if not mid_sys:
        print("System must be specified, use --csp or --tmc")
        return 1

    if not ctl_dev_name:
        ctl_dev_name = cfg_data[mid_sys]["control_device"]
    if not sub_dev_name:
        sub_dev_name = cfg_data[mid_sys]["subarray_device"]
    if not leaf_dev_name:
        leaf_dev_name = cfg_data[mid_sys]["leafnode_device"]
    if not resource_data:
        resource_data = cfg_data[mid_sys]["subarray_resources"]
    if not long_cmds < 0:
        long_cmds = int(cfg_data[mid_sys]["long_run_cmds"])
    if not bite_cmd:
        bite_cmd = cfg_data[mid_sys]["bite_cmd"]

    show_config_json(mid_sys, cfg_data)
    if show_cfg:
        return 1

    ns_sdp_name = f"{ns_name}-sdp"

    # Set the Tango host
    tango_fqdn = f"{svc_name}.{ns_name}.svc.{cluster_domain}"
    # print("Tango database FQDN is %s" % tango_fqdn)
    tango_port = 10000
    tango_host = f"{tango_fqdn}:{tango_port}"
    # print("Tango host %s" % tango_host)
    os.environ["TANGO_HOST"] = tango_host

    rc = check_tango(tango_fqdn, tango_port)
    if rc or show_tango:
        return 1
    progrs = 0
    if show_obs:
        rc = show_observation_status(sub_dev_name)
        progrs += 1
    if show_long:
        rc = show_long_running_commands(sub_dev_name)
        progrs += 1

    # Start Tango devices
    if dev_start:
        rc, sub_dev = do_startup(
            ctl_dev_name,
            timeout,
            dev_sim,
            show_status,
            sub_dev_name,
            resource_data,
            long_cmds,
        )
        progrs += 1
    # Control Tango devices
    if dev_ctrl:
        rc = do_control(
            sub_dev_name,
            sub_dev,
            ns_name,
            databaseds_name,
            ns_sdp_name,
            leaf_dev_name,
            bite_cmd,
        )
        progrs += 1
    # Stop Tango devices
    if dev_stop:
        rc = do_shutdown(
            ctl_dev_name,
            sub_dev_name,
            tear_down,
        )
        progrs += 1

    if not progrs:
        print("Nothing to do")
        print(f"Run '{os.path.basename(y_arg[0])} --help'")
        rc = 1

    return rc


if __name__ == "__main__":
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        pass
