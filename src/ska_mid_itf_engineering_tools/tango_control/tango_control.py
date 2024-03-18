"""Read all information about Tango devices in a Kubernetes cluster."""

import json
import logging
import os
import socket
from typing import Any

import tango

from ska_mid_itf_engineering_tools.tango_control.read_tango_devices import TangoctlDevicesBasic
from ska_mid_itf_engineering_tools.tango_control.test_tango_script import TangoScript


class TangoControl:
    """Connect to Tango environment and retrieve information."""

    def __init__(self, logger: logging.Logger):
        """
        Get the show on the road.

        :param logger: logging handle
        """
        self.logger = logger

    def read_input_file(self, input_file: str | None, tgo_name: str | None, dry_run: bool) -> None:
        """
        Read instructions from JSON file.

        :param input_file: input file name
        :param tgo_name: device name
        :param dry_run: flag for dry run
        """
        if input_file is None:
            return
        inf: str = input_file
        tgo_script = TangoScript(self.logger, inf, tgo_name, dry_run)
        tgo_script.run()

    def check_tango(
        self,
        tango_host: str,
        quiet_mode: bool,
        tango_port: int = 10000,
    ) -> int:
        """
        Check Tango host address.

        :param tango_fqdn: fully qualified domain name
        :param quiet_mode: flag to suppress extra output
        :param tango_port: port number
        :return: error condition
        """
        tango_fqdn: str
        tport: int
        if ":" in tango_host:
            tango_fqdn = tango_host.split(":")[0]
            tport = int(tango_host.split(":")[1])
        else:
            tango_fqdn = tango_host
            tport = tango_port
        self.logger.info("Check Tango host %s:%d", tango_fqdn, tport)
        try:
            tango_addr = socket.gethostbyname_ex(tango_fqdn)
            tango_ip = tango_addr[2][0]
        except socket.gaierror as e:
            self.logger.error("Could not read address %s : %s" % (tango_fqdn, e))
            return 1
        if not quiet_mode:
            print(f"TANGO_HOST={tango_fqdn}:{tport}")
            print(f"TANGO_HOST={tango_ip}:{tport}")
        return 0

    def get_tango_classes(
        self,
        fmt: str,
        evrythng: bool,
        quiet_mode: bool,
        cfg_data: Any,
        tgo_name: str | None,
    ) -> dict:
        """
        Read tango classes.

        :param fmt: output format
        :param evrythng: get commands and attributes regadrless of state
        :param quiet_mode: flag for displaying progress bars
        :param cfg_data: configuration data in JSON format
        :param tgo_name: device name
        :return: dictionary with devices
        """
        try:
            devices = TangoctlDevicesBasic(
                self.logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
            )
        except tango.ConnectionFailed:
            self.logger.error("Tango connection failed")
            return {}
        devices.read_config()
        dev_classes = devices.get_classes()
        return dev_classes

    def list_classes(
        self,
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
        self.logger.info("List classes")
        if fmt == "json":
            self.logger.info("Get device classes")
            try:
                devices = TangoctlDevicesBasic(
                    self.logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
                )
            except tango.ConnectionFailed:
                self.logger.error("Tango connection failed")
                return 1
            devices.read_config()
            dev_classes = devices.get_classes()
            print(json.dumps(dev_classes, indent=4))
        return 0

    def list_devices(
        self,
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
            self.logger.info("List devices (%s) with name %s", fmt, tgo_name)
            try:
                devices = TangoctlDevicesBasic(
                    self.logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
                )
            except tango.ConnectionFailed:
                self.logger.error("Tango connection failed")
                return 1
            devices.read_config()
            if fmt == "json":
                devices.print_json(0)
            elif fmt == "yaml":
                devices.print_yaml(0)
            else:
                devices.print_txt_list()
        elif disp_action == 5:
            self.logger.info("List device classes (%s)", fmt)
            try:
                devices = TangoctlDevicesBasic(
                    self.logger, quiet_mode, evrythng, cfg_data, tgo_name, fmt
                )
            except tango.ConnectionFailed:
                self.logger.error("Tango connection failed")
                return 1
            devices.read_config()
            devices.print_txt_classes()
        else:
            pass
        return 0

    def read_input_files(self, json_dir: str, quiet_mode: bool = True) -> int:
        """
        Read info from script files.

        :param json_dir: directory with script files
        :param quiet_mode: turn off progress bar
        :return: error condition
        """
        rv = 0
        self.logger.info("List JSON and YAML files in %s", json_dir)
        relevant_path = json_dir
        included_extensions = ["json", "yaml"]
        file_names = [
            fn
            for fn in os.listdir(relevant_path)
            if any(fn.endswith(ext) for ext in included_extensions)
        ]
        if not file_names:
            self.logger.info("No JSON and YAML files found in %s", json_dir)
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
                        self.logger.info("File %s is not a tangoctl input file", file_name)
                        rv += 1
                except json.decoder.JSONDecodeError:
                    self.logger.info("File %s is not a JSON file", file_name)
        return rv
