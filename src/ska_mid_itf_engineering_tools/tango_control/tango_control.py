"""Read all information about Tango devices in a Kubernetes cluster."""

import json
import logging
import os
import socket
from typing import Any

import tango
import yaml

from ska_mid_itf_engineering_tools.k8s_info.get_k8s_info import KubernetesControl
from ska_mid_itf_engineering_tools.tango_control.read_tango_devices import TangoctlDevicesBasic
from ska_mid_itf_engineering_tools.tango_control.test_tango_script import TangoScript

logging.basicConfig(level=logging.WARNING)
_module_logger = logging.getLogger("tango_control")
_module_logger.setLevel(logging.WARNING)


def read_input_file(input_file: str | None, tgo_name: str | None, dry_run: bool) -> None:
    """
    Read instructions from JSON file.

    :param input_file: input file name
    :param tgo_name: device name
    :param dry_run: flag for dry run
    """
    if input_file is None:
        return
    inf: str = input_file
    tgo_script = TangoScript(_module_logger, inf, tgo_name, dry_run)
    tgo_script.run()


def check_tango(
    tango_fqdn: str,
    quiet_mode: bool,
    tango_port: int = 10000,
    logger: logging.Logger = _module_logger,
) -> int:
    """
    Check Tango host address.

    :param tango_fqdn: fully qualified domain name
    :param quiet_mode: flag to suppress extra output
    :param tango_port: port number
    :param logger: logging handle
    :return: error condition
    """
    logger.info("Check Tango host %s:%d", tango_fqdn, tango_port)
    try:
        tango_addr = socket.gethostbyname_ex(tango_fqdn)
        tango_ip = tango_addr[2][0]
    except socket.gaierror as e:
        logger.error("Could not read address %s : %s" % (tango_fqdn, e))
        return 1
    if not quiet_mode:
        print(f"TANGO_HOST={tango_fqdn}:{tango_port}")
        print(f"TANGO_HOST={tango_ip}:{tango_port}")
    return 0


def get_namespaces_list(logger: logging.Logger = _module_logger) -> list:
    """
    Read namespaces in Kubernetes cluster.

    :param logger: logging handle
    :return: list with devices
    """
    k8s = KubernetesControl(logger)
    ns_list = k8s.get_namespaces_list()
    logger.info("Read %d namespaces", len(ns_list))
    return ns_list


def get_namespaces_dict(logger: logging.Logger = _module_logger) -> dict:
    """
    Read namespaces in Kubernetes cluster.

    :param logger: logging handle
    :return: dictionary with devices
    """
    k8s = KubernetesControl(logger)
    ns_dict = k8s.get_namespaces_dict()
    logger.info("Read %d namespaces", len(ns_dict))
    return ns_dict


def show_namespaces(output_file: str | None, fmt: str) -> None:
    """
    Display namespaces in Kubernetes cluster.

    :param output_file: output file name
    :param fmt: output format
    """
    if fmt == "json":
        ns_dict = get_namespaces_dict()
        if output_file is not None:
            _module_logger.info("Write output file %s", output_file)
            with open(output_file, "w") as outf:
                outf.write(json.dumps(ns_dict, indent=4))
        else:
            print(json.dumps(ns_dict, indent=4))
    elif fmt == "yaml":
        ns_dict = get_namespaces_dict()
        if output_file is not None:
            _module_logger.info("Write output file %s", output_file)
            with open(output_file, "w") as outf:
                outf.write(yaml.dump(ns_dict))
        else:
            print(yaml.dump(ns_dict))
    else:
        ns_list = get_namespaces_list()
        print(f"Namespaces : {len(ns_list)}")
        for ns_name in ns_list:
            print(f"\t{ns_name}")


def get_pods_dict(ns_name: str | None, logger: logging.Logger = _module_logger) -> dict:
    """
    Read pods in Kubernetes namespace.

    :param ns_name: namespace name
    :param logger: logging handle
    :return: dictionary with devices
    """
    k8s = KubernetesControl(logger)
    pods_dict = k8s.get_pods(ns_name, None)
    logger.info("Read %d pods", len(pods_dict))
    return pods_dict


def print_pods(ns_name: str | None, quiet_mode: bool) -> None:  # noqa: C901
    """
    Display pods in Kubernetes namespace.

    :param ns_name: namespace name
    :param quiet_mode: flag to suppress extra output
    """
    if ns_name is None:
        _module_logger.error("K8S namespace not specified")
        return
    k8s = KubernetesControl(_module_logger)
    pods_dict = get_pods_dict(ns_name)
    print(f"Pods : {len(pods_dict)}")
    for pod_name in pods_dict:
        print(f"{pod_name}")
        if not quiet_mode:
            resps = k8s.exec_command(ns_name, pod_name, ["ps", "-ef"])
            if not resps:
                pass
            elif "\n" in resps:
                for resp in resps.split("\n"):
                    _module_logger.debug("Got '%s'", resp)
                    if not resp:
                        pass
                    elif resp[-6:] == "ps -ef":
                        pass
                    elif resp[0:3] == "UID":
                        pass
                    elif resp[0:3] == "PID":
                        pass
                    # elif "nginx" in resp:
                    #     pass
                    elif resp[0:5] in ("tango", "root ", "mysql") or resp[0:3] == "100":
                        respl = resp.split()
                        print(f"\t* {respl[0]:8} {' '.join(respl[7:])}")
                    else:
                        print(f"\t  {resp}")
            else:
                print(f"\t- {resps}")


def get_pods_json(ns_name: str | None) -> dict:
    """
    Read pods in Kubernetes namespace.

    :param ns_name: namespace name
    :return: dictionary with pod information
    """
    pods: dict = {}
    if ns_name is None:
        _module_logger.error("K8S namespace not specified")
        return pods
    k8s = KubernetesControl(_module_logger)
    pods_list = k8s.get_pods(ns_name, None)
    _module_logger.info("Found %d pods running in namespace %s", len(pods_list), ns_name)
    for pod_name in pods_list:
        _module_logger.info("Read processes running in pod %s", pod_name)
        resps = k8s.exec_command(ns_name, pod_name, ["ps", "-ef"])
        pods[pod_name] = []
        if not resps:
            pass
        elif "\n" in resps:
            for resp in resps.split("\n"):
                if not resp:
                    pass
                elif resp[-6:] == "ps -ef":
                    pass
                elif resp[0:3] == "UID":
                    pass
                elif resp[0:3] == "PID":
                    pass
                # elif "nginx" in resp:
                #     pass
                else:
                    pods[pod_name].append(resp)
        else:
            pods[pod_name].append(resps)
    return pods


def show_pods(
    ns_name: str | None, quiet_mode: bool, output_file: str | None, fmt: str | None
) -> None:
    """
    Display pods in Kubernetes namespace.

    :param ns_name: namespace name
    :param quiet_mode: flag to suppress progress bar etc.
    :param output_file: output file name
    :param fmt: output format
    """
    if fmt == "json":
        pods = get_pods_json(ns_name)
        if output_file is not None:
            _module_logger.info("Write output file %s", output_file)
            with open(output_file, "w") as outf:
                outf.write(json.dumps(pods, indent=4))
        else:
            print(json.dumps(pods, indent=4))
    elif fmt == "yaml":
        pods = get_pods_json(ns_name)
        if output_file is not None:
            _module_logger.info("Write output file %s", output_file)
            with open(output_file, "w") as outf:
                outf.write(yaml.dump(pods))
        else:
            print(yaml.dump(pods))
    else:
        show_pods(ns_name, quiet_mode, output_file, fmt)


def get_tango_classes(
    fmt: str,
    evrythng: bool,
    quiet_mode: bool,
    cfg_data: Any,
    tgo_name: str | None,
    logger: logging.Logger = _module_logger,
) -> dict:
    """
    Read tango classes.

    :param fmt: output format
    :param evrythng: get commands and attributes regadrless of state
    :param quiet_mode: flag for displaying progress bars
    :param cfg_data: configuration data in JSON format
    :param tgo_name: device name
    :param logger: logging handle
    :return: dictionary with devices
    """
    try:
        devices = TangoctlDevicesBasic(
            _module_logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
        )
    except tango.ConnectionFailed:
        _module_logger.error("Tango connection failed")
        return {}
    devices.read_config()
    dev_classes = devices.get_classes()
    return dev_classes


def list_classes(
    fmt: str,
    evrythng: bool,
    quiet_mode: bool,
    cfg_data: Any,
    tgo_name: str | None,
) -> int:
    """
    Get device classes.

    :param fmt: output format
    :param evrythng: get commands and attributes regadrless of state
    :param quiet_mode: flag for displaying progress bars
    :param cfg_data: configuration data in JSON format
    :param tgo_name: device name
    :return: error condition
    """
    _module_logger.info("List classes")
    if fmt == "json":
        _module_logger.info("Get device classes")
        try:
            devices = TangoctlDevicesBasic(
                _module_logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
            )
        except tango.ConnectionFailed:
            _module_logger.error("Tango connection failed")
            return 1
        devices.read_config()
        dev_classes = devices.get_classes()
        print(json.dumps(dev_classes, indent=4))
    return 0


def list_devices(
    file_name: str | None,
    fmt: str,
    evrythng: bool,
    quiet_mode: bool,
    disp_action: int,
    cfg_data: Any,
    tgo_name: str | None,
) -> int:
    """
    List Tango devices.

    :param file_name: output file name
    :param fmt: output format
    :param evrythng: get commands and attributes regadrless of state
    :param quiet_mode: flag for displaying progress bars
    :param disp_action: flag for output format
    :param cfg_data: configuration data in JSON format
    :param tgo_name: device name
    :return: error condition
    """
    if disp_action == 4:
        _module_logger.info("List devices (%s)", fmt)
        try:
            devices = TangoctlDevicesBasic(
                _module_logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
            )
        except tango.ConnectionFailed:
            _module_logger.error("Tango connection failed")
            return 1
        devices.read_config()
        if fmt == "json":
            devices.print_json(0)
        elif fmt == "yaml":
            devices.print_yaml(0)
        else:
            devices.print_txt_list()
    elif disp_action == 5:
        _module_logger.info("List device classes (%s)", fmt)
        try:
            devices = TangoctlDevicesBasic(
                _module_logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
            )
        except tango.ConnectionFailed:
            _module_logger.error("Tango connection failed")
            return 1
        devices.read_config()
        devices.print_txt_classes()
    else:
        pass
    return 0


def read_input_files(
    json_dir: str, quiet_mode: bool = True, logger: logging.Logger = _module_logger
) -> int:
    """
    Read info from script files.

    :param json_dir: directory with script files
    :param quiet_mode: turn off progress bar
    :param logger: logging handle
    :return: error condition
    """
    rv = 0
    _module_logger.info("List JSON and YAML files in %s", json_dir)
    relevant_path = json_dir
    included_extensions = ["json", "yaml"]
    file_names = [
        fn
        for fn in os.listdir(relevant_path)
        if any(fn.endswith(ext) for ext in included_extensions)
    ]
    if not file_names:
        _module_logger.info("No JSON and YAML files found in %s", json_dir)
        return 1
    for file_name in file_names:
        file_name = os.path.join(json_dir, file_name)
        with open(file_name) as cfg_file:
            try:
                cfg_data = json.load(cfg_file)
                try:
                    description = cfg_data["description"]
                    if not quiet_mode:
                        print(f"{file_name:40} {description}")
                except KeyError:
                    _module_logger.info("File %s is not a tangoctl input file", file_name)
                    rv += 1
            except json.decoder.JSONDecodeError:
                _module_logger.info("File %s is not a JSON file", file_name)
    return rv
