"""Read and display Tango stuff."""
import json
import logging
import os
import sys
from typing import Any

import tango
import yaml

from ska_mid_itf_engineering_tools.tango_control.read_tango_device import (
    TangoctlDevice,
    TangoctlDeviceBasic,
)
from ska_mid_itf_engineering_tools.tango_control.tango_json import TangoJsonReader


def progress_bar(
    iterable: list | dict,
    show: bool,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 100,
    fill: str = "*",
    print_end: str = "\r",
) -> Any:
    r"""
    Call this in a loop to create a terminal progress bar.

    :param iterable: Required - iterable object (Iterable)
    :param show: print the actual thing
    :param prefix: prefix string
    :param suffix: suffix string
    :param decimals: positive number of decimals in percent complete
    :param length: character length of bar
    :param fill: fill character for bar
    :param print_end: end character (e.g. "\r", "\r\n")
    :yields: the next one in line
    """

    def print_progress_bar(iteration: Any) -> None:
        """
        Progress bar printing function.

        :param iteration: the thing
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + "-" * (length - filled_length)
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=print_end)

    if show:
        total = len(iterable)
        # Do not divide by zero
        if total == 0:
            total = 1
        # Initial call
        print_progress_bar(0)
        # Update progress bar
        for i, item in enumerate(iterable):
            yield item
            print_progress_bar(i + 1)
        # Erase line upon completion
        sys.stdout.write("\033[K")
    else:
        # Nothing to see here
        for i, item in enumerate(iterable):
            yield item


class TangoctlDevicesBasic:
    """Compile a dictionary of available Tango devices."""

    devices: dict = {}

    def __init__(  # noqa: C901s
        self,
        logger: logging.Logger,
        evrythng: bool,
        cfg_data: Any,
        tgo_name: str | None,
        fmt: str,
    ):
        """
        Read list of Tango devices.

        :param logger: logging handle
        :param evrythng: read and display the whole thing
        :param cfg_data: configuration data
        :param fmt: output format
        :param tgo_name: device name
        :raises Exception: database connect failed
        """
        self.logger = logger
        # Get Tango database host
        tango_host = os.getenv("TANGO_HOST")
        # Connect to database
        try:
            database = tango.Database()
        except Exception as terr:
            self.logger.error("Could not connect to Tango database %s", tango_host)
            raise terr

        # Read devices
        device_list = sorted(database.get_device_exported("*").value_string)
        self.logger.info(f"{len(device_list)} devices available")

        if tgo_name:
            tgo_name = tgo_name.lower()

        self.fmt = fmt
        prog_bar: bool = True
        if self.fmt == "md":
            prog_bar = False
        if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
            prog_bar = False
        for device in progress_bar(
            device_list,
            prog_bar,
            prefix="Read exported devices :",
            suffix="complete",
            decimals=0,
            length=100,
        ):
            if not evrythng:
                chk_fail = False
                for dev_chk in cfg_data["ignore_device"]:
                    chk_len = len(dev_chk)
                    if device[0:chk_len] == dev_chk:
                        chk_fail = True
                        break
                if chk_fail:
                    self.logger.debug("'%s' matches '%s'", device, cfg_data["ignore_device"])
                    continue
            if tgo_name:
                ichk = device.lower()
                if tgo_name not in ichk:
                    self.logger.info("Ignore device %s", device)
                    continue
            new_dev = TangoctlDeviceBasic(logger, device)
            self.devices[device] = new_dev

    def read_config(self) -> None:
        """Read additional data."""
        self.logger.info("Read %d devices", len(self.devices))
        prog_bar: bool = True
        if self.fmt == "md":
            prog_bar = False
        if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
            prog_bar = False
        for device in progress_bar(
            self.devices,
            prog_bar,
            prefix="Read config :",
            suffix="complete",
            decimals=0,
            length=100,
        ):
            self.devices[device].read_config()

    def print_txt_list(self) -> None:
        """Print list of devices."""
        self.logger.info("List %d devices", len(self.devices))
        print(f"{'DEVICE NAME':40} {'STATE':10} {'ADMIN':11} {'VERSION':8} CLASS")
        for device in self.devices:
            self.devices[device].print_list()


class TangoctlDevices(TangoctlDevicesBasic):
    """Compile a dictionary of available Tango devices."""

    devices: dict = {}
    attribs_found: list = []
    tgo_space: str

    def __init__(  # noqa: C901s
        self,
        logger: logging.Logger,
        kube_namespace: str | None,
        evrythng: bool,
        cfg_data: dict,
        tgo_name: str | None,
        tgo_attrib: str | None,
        tgo_cmd: str | None,
        tgo_prop: str | None,
        tango_port: int,
        output_file: str | None,
        fmt: str = "json",
    ):
        """
        Get a dict of devices.

        :param logger: logging handle
        :param kube_namespace: Kubernetes namespace
        :param cfg_data: configuration data in JSON format
        :param evrythng: get commands and attributes regadrless of state
        :param tgo_name: filter device name
        :param tgo_attrib: filter attribute name
        :param tgo_cmd: filter command name
        :param tgo_prop: filter property name
        :param tango_port: device port
        :param output_file: output file name
        :param fmt: output format
        :raises Exception: when database connect fails
        """
        self.logger = logger
        self.output_file = output_file
        self.logger.info(
            "Devices %s : attribute %s command %s property %s",
            tgo_name,
            tgo_attrib,
            tgo_cmd,
            tgo_prop,
        )
        # Get Tango database host
        tango_host = os.getenv("TANGO_HOST")
        if kube_namespace is not None:
            self.tgo_space = f"namespace {kube_namespace}"
        else:
            self.tgo_space = f"host {tango_host}"

        self.delimiter = cfg_data["delimiter"]
        self.run_commands = cfg_data["run_commands"]
        self.logger.info("Run commands %s", self.run_commands)
        self.run_commands_name = cfg_data["run_commands_name"]
        self.logger.info("Run commands with name %s", self.run_commands_name)

        if tango_port:
            trl = f"tango://127.0.0.1:{tango_port}/{tgo_name}#dbase=no"
            new_dev = TangoctlDevice(logger, trl, tgo_attrib, tgo_cmd, tgo_prop)
            self.devices[tgo_name] = new_dev
        else:
            # Connect to database
            try:
                database = tango.Database()
            except Exception as terr:
                self.logger.error("Could not connect to Tango database %s", tango_host)
                raise terr

            # Read devices
            device_list = sorted(database.get_device_exported("*").value_string)
            self.logger.info("Read %d devices available", len(device_list))

            prog_bar: bool = True
            if fmt == "md" and output_file is None:
                prog_bar = False
            if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
                prog_bar = False
            for device in progress_bar(
                device_list,
                prog_bar,
                prefix="Read exported devices:",
                suffix="Complete",
                length=100,
            ):
                # Check device name against mask
                if not evrythng:
                    chk_fail = False
                    for dev_chk in cfg_data["ignore_device"]:
                        chk_len = len(dev_chk)
                        if device[0:chk_len] == dev_chk:
                            chk_fail = True
                            break
                    if chk_fail:
                        self.logger.debug("'%s' matches '%s'", device, cfg_data["ignore_device"])
                        continue
                if tgo_name:
                    ichk = device.lower()
                    if tgo_name not in ichk:
                        self.logger.info("Ignore device %s", device)
                        continue
                try:
                    new_dev = TangoctlDevice(logger, device, tgo_attrib, tgo_cmd, tgo_prop)
                except tango.ConnectionFailed:
                    logger.info("Could not read device %s", device)
                    continue
                if tgo_attrib:
                    attribs_found = new_dev.check_for_attribute(tgo_attrib)
                    if attribs_found:
                        self.logger.info("Device %s matched attributes %s", device, attribs_found)
                        self.devices[device] = new_dev
                    else:
                        logger.debug("Skip device %s", device)
                else:
                    self.logger.debug("Add device %s", device)
                    self.devices[device] = new_dev
        logger.debug("Read %d devices", len(self.devices))

    def read_attribute_values(self) -> None:
        """Read device data."""
        for device in self.devices:
            self.devices[device].read_attribute_value()

    def read_command_values(self) -> None:
        """Read device data."""
        for device in self.devices:
            self.devices[device].read_command_value(self.run_commands, self.run_commands_name)

    def read_property_values(self) -> None:
        """Read device data."""
        for device in self.devices:
            self.devices[device].read_property_value()

    def read_device_values(self) -> None:
        """Read device data."""
        self.read_attribute_values()
        self.read_property_values()
        self.logger.info("Read devices %s", self.devices)

    def get_json(self) -> dict:
        """
        Read device data.

        :return: dictionary
        """
        devsdict = {}
        for device in self.devices:
            devsdict[device] = self.devices[device].get_json(self.delimiter)
        return devsdict

    def print_txt_list(self) -> None:
        """Print list of devices."""
        self.logger.info("List %d devices", len(self.devices))
        if self.output_file is not None:
            with open(self.output_file, "w") as outf:
                for device in self.devices:
                    outf.write(f"{device}\n")
        else:
            for device in self.devices:
                print(f"{device}")

    def print_txt(self, disp_action: int) -> None:
        """
        Print in text format.

        :param disp_action: display control flag
        """
        if disp_action == 4:
            self.print_txt_list()
        elif disp_action == 3:
            devsdict = self.get_json()
            json_reader = TangoJsonReader(self.logger, self.tgo_space, devsdict, self.output_file)
            json_reader.print_txt_quick()
        else:
            devsdict = self.get_json()
            json_reader = TangoJsonReader(self.logger, self.tgo_space, devsdict, self.output_file)
            json_reader.print_txt_all()

    def print_json(self, disp_action: int) -> None:
        """
        Print in JSON format.

        :param disp_action: display control flag
        """
        devsdict = self.get_json()
        if self.output_file is not None:
            with open(self.output_file, "w") as outf:
                outf.write(json.dumps(devsdict, indent=4))
        else:
            print(json.dumps(devsdict, indent=4))

    def print_markdown(self, disp_action: int) -> None:
        """
        Print in JSON format.

        :param disp_action: display control flag
        """
        self.logger.info("Markdown")
        devsdict = self.get_json()
        json_reader = TangoJsonReader(self.logger, self.tgo_space, devsdict, self.output_file)
        json_reader.print_markdown_all()

    def print_yaml(self, disp_action: int) -> None:
        """
        Print in YAML format.

        :param disp_action: display control flag
        """
        self.logger.info("YAML")
        devsdict = self.get_json()
        if self.output_file is not None:
            with open(self.output_file, "w") as outf:
                outf.write(yaml.dump(devsdict))
        else:
            print(yaml.dump(devsdict))
