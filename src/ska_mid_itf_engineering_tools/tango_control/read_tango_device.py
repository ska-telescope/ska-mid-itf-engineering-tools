"""Read and display Tango stuff."""
import json
import logging
import sys
from typing import Any

import numpy
import tango


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


class TangoctlDeviceBasic:
    """Compile a basic dictionary for a Tango device."""

    logger: logging.Logger
    dev: tango.DeviceProxy
    dev_ok: bool
    info: str = "N/A"
    version: str = "N/A"
    status: str = "N/A"
    adminMode: Any = None
    adminModeStr: str = "N/A"
    dev_class: str = "N/A"
    dev_state: Any = None
    dev_str: str = "N/A"
    list_values: list = []

    def __init__(  # noqa: C901
        self,
        logger: logging.Logger,
        device: str,
        list_values: dict = {},
    ):
        """
        Iniltialise the thing.

        :param logger: logging handle
        :param device: device name
        """
        self.logger = logger
        self.logger.debug("Open device %s", device)
        self.dev = tango.DeviceProxy(device)
        try:
            self.dev_name = self.dev.name()
        except tango.DevFailed:
            self.dev_name = device
        try:
            self.dev_ok = True
        except tango.ConnectionFailed:
            self.logger.info("Could not read device %s", device)
            self.dev_name = "N/A"
            self.dev_ok = False
        self.list_values = list_values

    def read_config(self) -> None:
        """Read additional data."""
        try:
            self.info = self.dev.info()
        except tango.DevFailed:
            self.logger.info("Could not read device %s", self.dev_name)
            return
        except tango.ConnectionFailed:
            self.logger.info("Could not read device %s", self.dev_name)
            return
        try:
            self.version = self.dev.versionId
        except AttributeError:
            self.version = "N/A"
        self.dev_state = self.dev.State()
        self.dev_str = f"{repr(self.dev_state).split('.')[3]}"
        if "adminMode" in self.list_values["attributes"]:
            try:
                self.adminMode = self.dev.adminMode
                # self.adminMode = self.dev.read_attribute("adminMode")
                self.logger.debug("Admin mode: %s", self.adminMode)
            except AttributeError:
                self.adminMode = "N/A"
            try:
                self.adminModeStr = str(self.adminMode).split(".")[-1]
            except IndexError:
                self.adminModeStr = str(self.adminMode)
        else:
            self.adminMode = "---"
        self.dev_class = self.dev.info().dev_class

    def print_list(self) -> None:
        """Print data."""
        print(
            f"{self.dev_name:40} {self.dev_str:10} {self.adminModeStr:11} {self.version:8}"
            f" {self.dev_class}"
        )


class TangoctlDevice(TangoctlDeviceBasic):
    """Compile a dictionary for a Tango device."""

    commands: dict = {}
    attributes: dict = {}
    properties: dict = {}
    command_config: Any
    attribs_found: list = []
    props_found: list = []
    cmds_found: list = []
    info: Any
    prog_bar: bool = True

    def __init__(  # noqa: C901
        self,
        logger: logging.Logger,
        device: str,
        tgo_attrib: str | None,
        tgo_cmd: str | None,
        tgo_prop: str | None,
    ):
        """
        Iniltialise the thing.

        :param logger: logging handle
        :param device: device name
        :param tgo_attrib: attribute filter
        :param tgo_cmd: command filter
        :param tgo_prop: property filter
        """
        super().__init__(logger, device)
        self.logger.info(
            "New device %s (attributes %s, commands %s, properties %s)",
            device,
            tgo_attrib,
            tgo_cmd,
            tgo_prop,
        )
        if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
            self.prog_bar = False
        if tgo_attrib:
            tgo_attrib = tgo_attrib.lower()
        try:
            cmds = sorted(self.dev.get_command_list())
        except tango.DevFailed:
            self.logger.info("Could not read commands for %s", device)
            cmds = []
        for cmd in cmds:
            if tgo_cmd:
                if tgo_cmd in cmd.lower():
                    self.logger.debug("Add command %s", cmd)
                    self.commands[cmd] = {}
            elif tgo_attrib or tgo_prop:
                # self.logger.debug("Skip commands")
                pass
            else:
                self.logger.debug("Add command %s", cmd)
                self.commands[cmd] = {}
        try:
            attribs = sorted(self.dev.get_attribute_list())
        except tango.DevFailed:
            self.logger.info("Could not read commands for %s", device)
            attribs = []
        for attrib in attribs:
            if tgo_attrib:
                if tgo_attrib in attrib.lower():
                    self.logger.debug("Add attribute %s", attrib)
                    self.attributes[attrib] = {}
                # else:
                #     self.logger.debug("Skip attribute %s", attrib)
            elif tgo_cmd or tgo_prop:
                # self.logger.debug("Skip attributes")
                pass
            else:
                self.logger.debug("Add attribute %s", attrib)
                self.attributes[attrib] = {}
        try:
            props = sorted(self.dev.get_property_list("*"))
        except tango.NonDbDevice:
            self.logger.info("Not reading properties in nodb mode")
            props = []
        for prop in props:
            if tgo_prop:
                if tgo_prop in prop.lower():
                    self.logger.debug("Add property %s", prop)
                    self.properties[prop] = {}
                # else:
                #     self.logger.debug("Skip property %s", prop)
            elif tgo_attrib or tgo_cmd:
                # self.logger.debug("Skip property")
                pass
            else:
                self.logger.debug("Add property %s", prop)
                self.properties[prop] = {}

        try:
            self.info = self.dev.info()
        except tango.DevFailed:
            self.logger.info("Could not read info from %s", device)
            self.info = None
        self.version: str
        try:
            self.version = self.dev.versionId
        except AttributeError:
            self.version = "N/A"
        self.logger.info(
            "Add device %s with %d attributes, %d commands and %d properties",
            device,
            len(self.attributes),
            len(self.commands),
            len(self.properties),
        )

    def read_config(self) -> None:
        """Read attribute and command configuration."""
        self.logger.info("Read config from device %s", self.dev_name)
        for attrib in self.attributes:
            self.logger.debug("Read attribute config from %s", attrib)
            try:
                self.attributes[attrib]["config"] = self.dev.get_attribute_config(attrib)
            except tango.DevFailed:
                self.logger.info("Could not not read attribute config %s", attrib)
                self.attributes[attrib]["config"] = None
        for cmd in self.commands:
            self.logger.debug("Read command config from %s", cmd)
            try:
                self.commands[cmd]["config"] = self.dev.get_command_config(cmd)
            except tango.DevFailed:
                self.logger.info("Could not not read command config %s", cmd)
                self.commands[cmd]["config"] = None

    def check_for_attribute(self, tgo_attrib: str | None) -> list:
        """
        Filter by attribute name.

        :param tgo_attrib: attribute name
        :return: list of device names matched
        """
        self.logger.debug(
            "Check %d attributes for %s : %s", len(self.attributes), tgo_attrib, self.attributes
        )
        self.attribs_found = []
        if not tgo_attrib:
            return self.attribs_found
        chk_attrib = tgo_attrib.lower()
        for attrib in self.attributes:
            if chk_attrib in attrib.lower():
                self.attribs_found.append(attrib)
        return self.attribs_found

    def check_for_command(self, tgo_cmd: str | None) -> list:
        """
        Filter by command name.

        :param tgo_cmd: command name
        :return: list of device names matched
        """
        self.logger.debug(
            "Check %d commands for %s : %s", len(self.commands), tgo_cmd, self.commands
        )
        self.cmds_found = []
        if not tgo_cmd:
            return self.attribs_found
        chk_cmd = tgo_cmd.lower()
        for cmd in self.commands:
            if chk_cmd in cmd.lower():
                self.cmds_found.append(cmd)
        return self.cmds_found

    def check_for_property(self, tgo_prop: str | None) -> list:
        """
        Filter by command name.

        :param tgo_cmd: property name
        :return: list of device names matched
        """
        self.logger.debug(
            "Check %d props for %s : %s", len(self.commands), tgo_prop, self.commands
        )
        self.props_found = []
        if not tgo_prop:
            return self.props_found
        chk_prop = tgo_prop.lower()
        for cmd in self.properties:
            if chk_prop in cmd.lower():
                self.props_found.append(cmd)
        return self.props_found

    def get_json(self, delimiter: str = ",") -> dict:  # noqa: C901
        """
        Convert internal values to JSON.

        :param delimiter: field are seperated by this
        :return: dictionary
        """

        def set_json_attribute() -> None:
            """Add attributes to dictionary."""
            self.logger.debug("Set attribute %s", attrib)
            devdict["attributes"][attrib] = {}
            devdict["attributes"][attrib]["data"] = {}
            if "value" in self.attributes[attrib]["data"]:
                data_val = self.attributes[attrib]["data"]["value"]
                self.logger.debug(
                    "Attribute %s data type %s: %s", attrib, type(data_val), data_val
                )
                if type(data_val) is dict:
                    devdict["attributes"][attrib]["data"]["value"] = {}
                    for key in data_val:
                        devdict["attributes"][attrib]["data"]["value"][key] = data_val[key]
                elif type(data_val) is numpy.ndarray:
                    devdict["attributes"][attrib]["data"]["value"] = data_val.tolist()
                elif type(data_val) is list:
                    devdict["attributes"][attrib]["data"]["value"] = data_val
                elif type(data_val) is tuple:
                    devdict["attributes"][attrib]["data"]["value"] = list(data_val)
                elif type(data_val) is str:
                    if not data_val:
                        devdict["attributes"][attrib]["data"]["value"] = ""
                    elif data_val[0] == "{" and data_val[-1] == "}":
                        devdict["attributes"][attrib]["data"]["value"] = json.loads(data_val)
                    else:
                        devdict["attributes"][attrib]["data"]["value"] = data_val
                else:
                    devdict["attributes"][attrib]["data"]["value"] = str(data_val)
            if "error" in self.attributes[attrib]:
                devdict["attributes"][attrib]["error"] = str(self.attributes[attrib]["error"])
            devdict["attributes"][attrib]["data"]["type"] = str(
                self.attributes[attrib]["data"]["type"]
            )
            devdict["attributes"][attrib]["data"]["data_format"] = str(
                self.attributes[attrib]["data"]["data_format"]
            )
            if self.attributes[attrib]["config"] is not None:
                devdict["attributes"][attrib]["config"] = {}
                devdict["attributes"][attrib]["config"]["description"] = self.attributes[attrib][
                    "config"
                ].description
                devdict["attributes"][attrib]["config"]["root_attr_name"] = self.attributes[
                    attrib
                ]["config"].root_attr_name
                devdict["attributes"][attrib]["config"]["format"] = self.attributes[attrib][
                    "config"
                ].format
                devdict["attributes"][attrib]["config"]["data_format"] = str(
                    self.attributes[attrib]["config"].data_format
                )
                devdict["attributes"][attrib]["config"]["disp_level"] = str(
                    self.attributes[attrib]["config"].disp_level
                )
                devdict["attributes"][attrib]["config"]["data_type"] = str(
                    self.attributes[attrib]["config"].data_type
                )
                devdict["attributes"][attrib]["config"]["display_unit"] = self.attributes[attrib][
                    "config"
                ].display_unit
                devdict["attributes"][attrib]["config"]["standard_unit"] = self.attributes[attrib][
                    "config"
                ].standard_unit
                devdict["attributes"][attrib]["config"]["writable"] = str(
                    self.attributes[attrib]["config"].writable
                )
                devdict["attributes"][attrib]["config"]["writable_attr_name"] = self.attributes[
                    attrib
                ]["config"].writable_attr_name

        def set_json_command() -> None:
            """Add commands to dictionary."""
            devdict["commands"][cmd] = {}
            if self.commands[cmd]["config"] is not None:
                devdict["commands"][cmd]["in_type"] = repr(self.commands[cmd]["config"].in_type)
                devdict["commands"][cmd]["in_type_desc"] = self.commands[cmd][
                    "config"
                ].in_type_desc
                devdict["commands"][cmd]["out_type"] = repr(self.commands[cmd]["config"].out_type)
                devdict["commands"][cmd]["out_type_desc"] = self.commands[cmd][
                    "config"
                ].out_type_desc

        def set_json_property() -> None:
            """Add properties to dictionary."""
            if "value" in self.properties[prop]:
                prop_val = self.properties[prop]["value"]
                devdict["properties"][prop] = {}
                # pylint: disable-next=c-extension-no-member
                if type(prop_val) is tango._tango.StdStringVector:
                    devdict["properties"][prop]["value"] = delimiter.join(prop_val)
                else:
                    devdict["properties"][prop]["value"] = prop_val

        self.read_config()

        devdict: dict = {}
        devdict["name"] = self.dev_name
        devdict["version"] = self.version
        try:
            devdict["versioninfo"] = self.dev.getversioninfo()
        except AttributeError:
            self.logger.info("Could not read version info")
            devdict["versioninfo"] = ["N/A"]
        try:
            devdict["adminMode"] = str(self.dev.adminMode)  # .split(".")[1]
        except IndexError:
            devdict["adminMode"] = self.dev.adminMode
        except AttributeError:
            devdict["adminMode"] = "N/A"
        if self.info is not None:
            devdict["info"] = {}
            devdict["info"]["dev_class"] = self.info.dev_class
            devdict["info"]["server_host"] = self.info.server_host
            devdict["info"]["server_id"] = self.info.server_id
        devdict["attributes"] = {}
        if self.attribs_found:
            for attrib in self.attribs_found:
                set_json_attribute()
        else:
            for attrib in self.attributes:
                set_json_attribute()
        devdict["commands"] = {}
        for cmd in self.commands:
            self.logger.debug("Set command %s", cmd)
            set_json_command()
        devdict["properties"] = {}
        for prop in self.properties:
            self.logger.debug("Set property %s", prop)
            set_json_property()
        self.logger.info("INFO: %s", devdict)
        return devdict

    def write_attribute_value(self, attrib: str, value: str) -> int:
        """
        Set value of attribute.

        :param attrib: attribute name
        :param value: attribute value
        :return: error condition
        """
        if attrib not in self.attributes:
            self.logger.error("Attribute %s not found in %s", attrib, self.attributes.keys())
            return 1
        devtype = self.attributes[attrib]["data"]["type"]
        wval: Any
        if devtype == "DevEnum":
            wval = int(value)
        else:
            wval = value
        self.logger.info("Set attribute %s (%s) to %s (%s)", attrib, devtype, wval, type(wval))
        self.dev.write_attribute(attrib, wval)
        return 0

    def read_attribute_value(self) -> None:
        """Read device attributes."""
        # for attrib in progress_bar(
        #     self.attributes,
        #     self.prog_bar,
        #     prefix="Read attributes :",
        #     suffix="complete",
        #     decimals=0,
        #     length=100,
        # ):
        for attrib in self.attributes:
            self.attributes[attrib]["data"] = {}
            try:
                attrib_data = self.dev.read_attribute(attrib)
            except tango.DevFailed as terr:
                err_msg = str(terr.args[-1].desc)
                self.logger.debug("Failed on attribute %s : %s", attrib, err_msg)
                self.attributes[attrib]["error"] = "<ERROR> " + err_msg
                self.attributes[attrib]["data"]["type"] = "N/A"
                self.attributes[attrib]["data"]["data_format"] = "N/A"
                continue
            self.logger.debug("Read attribute %s : %s", attrib, attrib_data)
            self.attributes[attrib]["data"]["value"] = attrib_data.value
            self.attributes[attrib]["data"]["type"] = str(attrib_data.type)
            self.attributes[attrib]["data"]["data_format"] = str(attrib_data.data_format)
            self.logger.info(
                "Read attribute %s data : %s", attrib, self.attributes[attrib]["data"]
            )

    def read_command_value(self, run_commands: list, run_commands_name: list) -> None:
        """
        Read device commands.

        :param run_commands: commands safe to run without parameters
        :param run_commands_name: commands safe to run with device name as parameter
        """
        for cmd in self.commands:
            if cmd in run_commands:
                self.commands[cmd]["value"] = self.dev.command_inout(cmd)
                self.logger.debug(
                    "Read command %s (%s) : %s",
                    cmd,
                    type(self.commands[cmd]["value"]),
                    self.commands[cmd]["value"],
                )
            elif cmd in run_commands_name:
                self.commands[cmd]["value"] = self.dev.command_inout(cmd, self.dev_name)
                self.logger.debug(
                    "Read command %s (%s) with arg %s : %s",
                    cmd,
                    type(self.commands[cmd]["value"]),
                    self.dev_name,
                    self.commands[cmd]["value"],
                )
            else:
                pass
        return

    def read_property_value(self) -> None:
        """Read device properties."""
        for prop in self.properties:
            self.properties[prop]["value"] = self.dev.get_property(prop)[prop]
            self.logger.debug("Read property %s : %s", prop, self.properties[prop]["value"])
        return

    def print_list_attribute(self) -> None:
        """Print data."""
        print(
            f"{self.dev_name:40} {self.dev_str:10} {self.adminModeStr:11} {self.version:8}"
            f" {self.dev_class:24} ",
            end="",
        )
        n = 0
        for attrib in self.attributes.keys():
            if n:
                print(f"{' ':40} {' ':10} {' ':11} {' ':8} {' ':24} ", end="")
            print(f"{attrib}")
            n += 1

    def print_list_command(self) -> None:
        """Print data."""
        print(
            f"{self.dev_name:40} {self.dev_str:10} {self.adminModeStr:11} {self.version:8}"
            f" {self.dev_class:24} ",
            end="",
        )
        n = 0
        for cmd in self.commands.keys():
            if n:
                print(f"{' ':40} {' ':10} {' ':11} {' ':8} {' ':24} ", end="")
            print(f"{cmd}")
            n += 1

    def print_list_property(self) -> None:
        """Print data."""
        print(
            f"{self.dev_name:40} {self.dev_str:10} {self.adminModeStr:11} {self.version:8}"
            f" {self.dev_class:24} ",
            end="",
        )
        n = 0
        for prop in self.properties.keys():
            if n:
                print(f"{' ':40} {' ':10} {' ':11} {' ':8} {' ':24} ", end="")
            print(f"{prop}")
            n += 1
