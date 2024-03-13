"""Read and display Tango stuff."""

import json
import logging
import sys
from typing import Any

import numpy
import tango

from ska_mid_itf_engineering_tools.tango_control.ska_jargon import find_jargon


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
    info: str = "---"
    version: str = "---"
    status: str = "---"
    adminMode: Any = None
    adminModeStr: str = "---"
    dev_name: str = "---"
    dev_class: str = "---"
    dev_state: Any = None
    dev_str: str = "---"
    list_values: dict = {}
    green_mode: Any = None
    dev_access: str
    dev_errors: list = []
    attribs: list
    cmds: list
    props: list

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
        :param list_values: dictionary with values to process
        """
        self.logger = logger
        self.logger.debug("Open device %s", device)
        self.dev = tango.DeviceProxy(device)
        try:
            self.dev_name = self.dev.name()
        except tango.DevFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read device name for %s ; %s", device, err_msg)
            self.dev_errors.append(f"Could not read name of {device} : {err_msg}")
            self.dev_name = f"{device} (N/A)"
        except tango.ConnectionFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read name for device %s", device)
            self.dev_name = f"{device} (N/A)"
            self.dev_errors.append(f"Could not read info : {err_msg}")
        self.list_values = list_values
        self.green_mode = str(self.dev.get_green_mode())
        self.dev_access = str(self.dev.get_access_control())
        # Read attributes
        try:
            self.attribs = sorted(self.dev.get_attribute_list())
        except tango.DevFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read attributes for %s", device)
            self.dev_errors.append(f"Could not read attributes : {err_msg}")
            self.attribs = []
        # Read commands
        try:
            self.cmds = sorted(self.dev.get_command_list())
        except tango.DevFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read commands for %s", device)
            self.dev_errors.append(f"Could not read commands : {err_msg}")
            self.cmds = []
        # Read properties
        try:
            self.props = sorted(self.dev.get_property_list("*"))
        except tango.NonDbDevice:
            self.logger.info("Not reading properties in nodb mode")
            self.props = []

    def read_config(self) -> None:  # noqa: C901
        """
        Read additional data.

        State, adminMode and versionId are specific to devices
        """
        try:
            self.info = self.dev.info()
        except tango.DevFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read device %s : %s", self.dev_name, err_msg)
            self.dev_errors.append(f"Could not read device : {err_msg}")
            return
        except tango.ConnectionFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read device %s : %s", self.dev_name, err_msg)
            self.dev_errors.append(f"Could not read device : {err_msg}")
            return
        # Read version ID, where applicable
        if "versionId" not in self.attribs:
            self.version = "---"
        elif "versionId" in self.list_values["attributes"]:
            try:
                self.version = self.dev.versionId
            except tango.CommunicationFailed as terr:
                err_msg = terr.args[0].desc.strip()
                self.logger.info("Could not read %s version : %s", self.dev_name, err_msg)
                self.dev_errors.append(f"Could not read {self.dev_name} name : {err_msg}")
                self.version = "N/A"
            except AttributeError as oerr:
                self.logger.info("Could not read %s version : %s", self.dev_name, str(oerr))
                self.version = "N/A"
            if self.version is None:
                self.version = "N/A"
        else:
            self.version = "---"
        # Read state, where applicable
        if "State" not in self.cmds:
            self.dev_state = "---"
        elif "State" in self.list_values["commands"]:
            try:
                self.dev_state = self.dev.State()
            except tango.CommunicationFailed as terr:
                err_msg = terr.args[0].desc.strip()
                self.logger.info("Could not read %s state : %s", self.dev_name, err_msg)
            except TypeError as oerr:
                self.logger.info("Could not read %s state : %s", self.dev_name, str(oerr))
                self.dev_state = "N/A"
        else:
            self.dev_state = "---"
        try:
            self.dev_str = f"{repr(self.dev_state).split('.')[3]}"
        except IndexError:
            self.dev_str = f"{repr(self.dev_state)}"
        # Read admin mode, where applicable
        if "adminMode" not in self.attribs:
            self.adminMode = "---"
        elif "adminMode" in self.list_values["attributes"]:
            try:
                self.adminMode = self.dev.adminMode
                self.logger.debug("Admin mode: %s", self.adminMode)
            except tango.CommunicationFailed as terr:
                err_msg = terr.args[0].desc.strip()
                self.logger.info("Could not read %s admin mode : %s", self.dev_name, err_msg)
            except AttributeError as oerr:
                self.logger.info("Could not read %s version : %s", self.dev_name, str(oerr))
                self.adminMode = "N/A"
            try:
                self.adminModeStr = str(self.adminMode).split(".")[-1]
            except IndexError as oerr:
                self.logger.info("Could not read %s version : %s", self.dev_name, str(oerr))
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
    quiet_mode: bool = True

    def __init__(  # noqa: C901
        self,
        logger: logging.Logger,
        quiet_mode: bool,
        device: str,
        tgo_attrib: str | None,
        tgo_cmd: str | None,
        tgo_prop: str | None,
    ):
        """
        Iniltialise the thing.

        :param logger: logging handle
        :param quiet_mode: flag for displaying progress bars
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
        self.quiet_mode = quiet_mode
        if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
            self.quiet_mode = True
        if tgo_attrib:
            tgo_attrib = tgo_attrib.lower()
        for cmd in self.cmds:
            if tgo_cmd:
                if tgo_cmd in cmd.lower():
                    self.logger.debug("Add command %s", cmd)
                    self.commands[cmd] = {}
            elif tgo_attrib or tgo_prop:
                pass
            else:
                self.logger.debug("Add command %s", cmd)
                self.commands[cmd] = {}
        for attrib in self.attribs:
            if tgo_attrib:
                if tgo_attrib in attrib.lower():
                    self.logger.debug("Add attribute %s", attrib)
                    self.attributes[attrib] = {}
            elif tgo_cmd or tgo_prop:
                pass
            else:
                self.logger.debug("Add attribute %s", attrib)
                self.attributes[attrib] = {}
        for prop in self.props:
            if tgo_prop:
                if tgo_prop in prop.lower():
                    self.logger.debug("Add property %s", prop)
                    self.properties[prop] = {}
            elif tgo_attrib or tgo_cmd:
                pass
            else:
                self.logger.debug("Add property %s", prop)
                self.properties[prop] = {}

        try:
            self.info = self.dev.info()
        except tango.DevFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read info from %s : %s", device, err_msg)
            self.dev_errors.append(f"Could not read info: {err_msg}")
            self.info = None
        self.version: str
        try:
            self.version = self.dev.versionId
        except AttributeError as oerr:
            self.logger.info("Could not read device %s version ID : %s", self.dev_name, str(oerr))
            self.version = "N/A"
        except tango.CommunicationFailed as terr:
            err_msg = terr.args[0].desc.strip()
            self.logger.info("Could not read device %s version ID : %s", self.dev_name, err_msg)
            self.version = "N/A"
        self.logger.info(
            "Add device %s with %d attributes, %d commands and %d properties",
            device,
            len(self.attributes),
            len(self.commands),
            len(self.properties),
        )
        self.jargon = find_jargon(self.dev_name)

    def read_config(self) -> None:
        """Read attribute and command configuration."""
        self.logger.info("Read config from device %s", self.dev_name)
        # Read attribute configuration
        for attrib in self.attributes:
            self.logger.debug("Read attribute config from %s", attrib)
            try:
                self.attributes[attrib]["config"] = self.dev.get_attribute_config(attrib)
            except tango.DevFailed as terr:
                err_msg = terr.args[0].desc.strip()
                self.logger.info("Could not not read attribute config %s : %s", attrib, err_msg)
                self.attributes[attrib]["error"] = err_msg
                self.attributes[attrib]["config"] = None
        # Read command configuration
        for cmd in self.commands:
            self.logger.debug("Read command config from %s", cmd)
            try:
                self.commands[cmd]["config"] = self.dev.get_command_config(cmd)
            except tango.DevFailed as terr:
                err_msg = terr.args[0].desc.strip()
                self.logger.info("Could not not read command config %s : %s", cmd, err_msg)
                self.attributes[cmd]["error"] = err_msg
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
            return self.cmds_found
        chk_cmd = tgo_cmd.lower()
        for cmd in self.commands:
            if chk_cmd in cmd.lower():
                self.cmds_found.append(cmd)
        return self.cmds_found

    def check_for_property(self, tgo_prop: str | None) -> list:
        """
        Filter by command name.

        :param tgo_prop: property name
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

    def make_json(self, delimiter: str = ",") -> dict:  # noqa: C901
        """
        Convert internal values to JSON.

        :param delimiter: field are seperated by this
        :return: dictionary
        """

        def set_json_attribute(attr_name: str) -> None:
            """
            Add attribute to dictionary.

            :param attr_name: attribute name
            """
            self.logger.debug("Set attribute %s", attr_name)
            try:
                devdict["aliases"] = self.dev.get_device_alias_list()
            except AttributeError as oerr:
                self.logger.debug("Could not read device %s alias : %s", self.dev_name, str(oerr))
                devdict["aliases"] = "N/A"
            devdict["attributes"][attr_name] = {}
            devdict["attributes"][attr_name]["data"] = {}
            if "error" in self.attributes[attr_name]:
                devdict["attributes"][attr_name]["error"] = self.attributes[attr_name]["error"]
            if "value" in self.attributes[attr_name]["data"]:
                data_val = self.attributes[attr_name]["data"]["value"]
                self.logger.debug(
                    "Attribute %s data type %s: %s", attr_name, type(data_val), data_val
                )
                if type(data_val) is dict:
                    devdict["attributes"][attr_name]["data"]["value"] = {}
                    for key in data_val:
                        devdict["attributes"][attr_name]["data"]["value"][key] = data_val[key]
                elif type(data_val) is numpy.ndarray:
                    devdict["attributes"][attr_name]["data"]["value"] = data_val.tolist()
                elif type(data_val) is list:
                    devdict["attributes"][attr_name]["data"]["value"] = data_val
                elif type(data_val) is tuple:
                    devdict["attributes"][attr_name]["data"]["value"] = list(data_val)
                elif type(data_val) is str:
                    if not data_val:
                        devdict["attributes"][attr_name]["data"]["value"] = ""
                    elif data_val[0] == "{" and data_val[-1] == "}":
                        devdict["attributes"][attr_name]["data"]["value"] = json.loads(data_val)
                    else:
                        devdict["attributes"][attr_name]["data"]["value"] = data_val
                else:
                    devdict["attributes"][attr_name]["data"]["value"] = str(data_val)
            if "error" in self.attributes[attr_name]:
                devdict["attributes"][attr_name]["error"] = str(
                    self.attributes[attr_name]["error"]
                )
            devdict["attributes"][attr_name]["data"]["type"] = str(
                self.attributes[attr_name]["data"]["type"]
            )
            devdict["attributes"][attr_name]["data"]["data_format"] = str(
                self.attributes[attr_name]["data"]["data_format"]
            )
            if self.attributes[attr_name]["config"] is not None:
                devdict["attributes"][attr_name]["config"] = {}
                devdict["attributes"][attr_name]["config"]["description"] = self.attributes[
                    attr_name
                ]["config"].description
                devdict["attributes"][attr_name]["config"]["root_attr_name"] = self.attributes[
                    attr_name
                ]["config"].root_attr_name
                devdict["attributes"][attr_name]["config"]["format"] = self.attributes[attr_name][
                    "config"
                ].format
                devdict["attributes"][attr_name]["config"]["data_format"] = str(
                    self.attributes[attr_name]["config"].data_format
                )
                devdict["attributes"][attr_name]["config"]["disp_level"] = str(
                    self.attributes[attr_name]["config"].disp_level
                )
                devdict["attributes"][attr_name]["config"]["data_type"] = str(
                    self.attributes[attr_name]["config"].data_type
                )
                devdict["attributes"][attr_name]["config"]["display_unit"] = self.attributes[
                    attr_name
                ]["config"].display_unit
                devdict["attributes"][attr_name]["config"]["standard_unit"] = self.attributes[
                    attr_name
                ]["config"].standard_unit
                devdict["attributes"][attr_name]["config"]["writable"] = str(
                    self.attributes[attr_name]["config"].writable
                )
                devdict["attributes"][attr_name]["config"]["writable_attr_name"] = self.attributes[
                    attr_name
                ]["config"].writable_attr_name

        def set_json_command(cmd_name: str) -> None:
            """
            Add commands to dictionary.

            :param cmd_name: command name
            """
            devdict["commands"][cmd_name] = {}
            if "error" in self.commands[cmd_name]:
                devdict["commands"][cmd_name]["error"] = self.commands[cmd_name]["error"]
            if self.commands[cmd_name]["config"] is not None:
                devdict["commands"][cmd_name]["in_type"] = repr(
                    self.commands[cmd_name]["config"].in_type
                )
                devdict["commands"][cmd_name]["in_type_desc"] = self.commands[cmd_name][
                    "config"
                ].in_type_desc
                devdict["commands"][cmd_name]["out_type"] = repr(
                    self.commands[cmd_name]["config"].out_type
                )
                devdict["commands"][cmd_name]["out_type_desc"] = self.commands[cmd_name][
                    "config"
                ].out_type_desc
                if "value" in self.commands[cmd_name]:
                    devdict["commands"][cmd_name]["value"] = self.commands[cmd_name]["value"]

        def set_json_property(prop_name: str) -> None:
            """
            Add properties to dictionary.

            :param prop_name: property name
            """
            if "value" in self.properties[prop_name]:
                prop_val = self.properties[prop_name]["value"]
                devdict["properties"][prop_name] = {}
                # pylint: disable-next=c-extension-no-member
                if type(prop_val) is tango._tango.StdStringVector:
                    devdict["properties"][prop_name]["value"] = delimiter.join(prop_val)
                else:
                    devdict["properties"][prop_name]["value"] = prop_val

        self.read_config()

        devdict: dict = {}
        devdict["name"] = self.dev_name
        if not self.quiet_mode:
            devdict["errors"] = self.dev_errors
        devdict["green_mode"] = self.green_mode
        devdict["version"] = self.version
        devdict["device_access"] = self.dev_access
        if self.jargon:
            devdict["acronyms"] = self.jargon
        if self.info is not None:
            devdict["info"] = {}
            devdict["info"]["dev_class"] = self.info.dev_class
            devdict["info"]["dev_type"] = self.info.dev_type
            devdict["info"]["doc_url"] = self.info.doc_url
            devdict["info"]["server_host"] = self.info.server_host
            devdict["info"]["server_id"] = self.info.server_id
            devdict["info"]["server_version"] = self.info.server_version
        devdict["attributes"] = {}
        if self.attribs_found:
            for attrib in self.attribs_found:
                set_json_attribute(attrib)
        else:
            # Run "for attrib in self.attribs:"
            for attrib in progress_bar(
                self.attribs,
                not self.quiet_mode,
                prefix=f"Read {len(self.attribs)} JSON attributes :",
                suffix="complete",
                decimals=0,
                length=100,
            ):
                set_json_attribute(attrib)
        devdict["commands"] = {}
        if self.commands:
            for cmd in self.commands:
                self.logger.debug("Set command %s", cmd)
                set_json_command(cmd)
        devdict["properties"] = {}
        if self.properties:
            for prop in self.properties:
                self.logger.debug("Set property %s", prop)
                set_json_property(prop)
        self.logger.debug("Read device : %s", devdict)
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
        for attrib in self.attributes:
            self.attributes[attrib]["data"] = {}
            try:
                attrib_data = self.dev.read_attribute(attrib)
            except tango.DevFailed as terr:
                err_msg = str(terr.args[-1].desc)
                self.logger.debug("Failed on attribute %s : %s", attrib, err_msg)
                self.attributes[attrib]["error"] = err_msg
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
                try:
                    self.commands[cmd]["value"] = self.dev.command_inout(cmd)
                except tango.ConnectionFailed as terr:
                    err_msg = terr.args[0].desc.strip()
                    self.logger.info("Could not run command %s : %s", cmd, err_msg)
                    self.commands[cmd]["value"] = "N/A"
                    self.commands[cmd]["error"] = err_msg
                except tango.DevFailed as terr:
                    err_msg = terr.args[0].desc.strip()
                    self.logger.info("Could not run command %s : %s", cmd, err_msg)
                    self.commands[cmd]["value"] = "N/A"
                    self.commands[cmd]["error"] = err_msg
                self.logger.info(
                    "Read command %s (%s) : %s",
                    cmd,
                    type(self.commands[cmd]["value"]),
                    self.commands[cmd]["value"],
                )
            elif cmd in run_commands_name:
                self.commands[cmd]["value"] = self.dev.command_inout(cmd, self.dev_name)
                self.logger.info(
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
            self.logger.info("Read property %s : %s", prop, self.properties[prop]["value"])
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
