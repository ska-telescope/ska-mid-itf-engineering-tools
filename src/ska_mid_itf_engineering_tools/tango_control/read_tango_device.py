"""Read and display Tango stuff."""
import logging
from typing import Any

import tango


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

    def __init__(  # noqa: C901
        self,
        logger: logging.Logger,
        device: str,
    ):
        """
        Iniltialise the thing.

        :param logger: logging handle
        :param device: device name
        """
        self.logger = logger
        self.logger.debug("Add device %s", device)
        self.dev_name = device
        self.dev = tango.DeviceProxy(device)
        try:
            self.dev_ok = True
        except tango.ConnectionFailed:
            self.logger.info("Could not read device %s", device)
            self.dev_name = "N/A"
            self.dev_ok = False

    def read_config(self) -> None:
        """Read additional data."""
        # if not self.dev_ok:
        #     return
        try:
            self.info = self.dev.info()
        except tango.ConnectionFailed:
            self.logger.info("Could not read device %s", self.dev_name)
            return
        try:
            self.version = self.dev.versionId
        except AttributeError:
            self.version = "N/A"
        self.dev_state = self.dev.State()
        self.dev_str = f"{repr(self.dev_state).split('.')[3]}"
        # self.adminMode = self.dev.read_attribute("adminMode")
        try:
            self.adminMode = self.dev.adminMode
        except AttributeError:
            self.adminMode = "N/A"
        try:
            self.adminModeStr = str(self.adminMode).split(".")[1]
        except IndexError:
            self.adminModeStr = str(self.adminMode)
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
        cmds = sorted(self.dev.get_command_list())
        for cmd in cmds:
            if tgo_cmd:
                if tgo_cmd in cmd.lower():
                    self.logger.debug("Add command %s", cmd)
                    self.commands[cmd] = {}
            elif tgo_attrib or tgo_prop:
                self.logger.debug("Skip commands")
            else:
                self.logger.debug("Add command %s", cmd)
                self.commands[cmd] = {}
            # self.commands[cmd]["config"] = None
        attribs = sorted(self.dev.get_attribute_list())
        for attrib in attribs:
            if tgo_attrib:
                if tgo_attrib in attrib.lower():
                    self.logger.debug("Add attribute %s", attrib)
                    self.attributes[attrib] = {}
                else:
                    self.logger.debug("Skip attribute %s", attrib)
            elif tgo_cmd or tgo_prop:
                self.logger.debug("Skip attributes")
            else:
                self.logger.debug("Add attribute %s", attrib)
                self.attributes[attrib] = {}
            # self.attributes[attrib]["config"] = None
        props = sorted(self.dev.get_property_list("*"))
        for prop in props:
            if tgo_prop:
                if tgo_prop in prop.lower():
                    self.logger.debug("Add property %s", prop)
                    self.properties[prop] = {}
                else:
                    self.logger.debug("Skip property %s", prop)
            elif tgo_attrib or tgo_cmd:
                self.logger.debug("Skip property")
            else:
                self.logger.debug("Add property %s", prop)
                self.properties[prop] = {}
        self.info: Any = self.dev.info()
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
        self.logger.info("Read config for device %s", self.dev_name)
        for attrib in self.attributes:
            self.logger.debug("Read attribute config for %s", attrib)
            try:
                self.attributes[attrib]["config"] = self.dev.get_attribute_config(attrib)
            except tango.DevFailed:
                self.logger.info("Could not not read attribute config %s", attrib)
                self.attributes[attrib]["config"] = None
        for cmd in self.commands:
            self.logger.debug("Read command config for %s", cmd)
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
        self.attribs_found: list = []
        if not tgo_attrib:
            return self.attribs_found
        for attrib in self.attributes:
            if tgo_attrib in attrib.lower():
                self.attribs_found.append(attrib)
        return self.attribs_found

    def get_json(self, delimiter: str) -> dict:  # noqa: C901
        """
        Convert internal values to JSON.

        :param delimiter: field are seperated by this
        :return: dictionary
        """

        def set_json_attribute() -> None:
            """Add attributes to dictionary."""
            devdict["attributes"][attrib] = {}
            if "value" in self.attributes[attrib]:
                devdict["attributes"][attrib]["value"] = str(self.attributes[attrib]["value"])
            if "error" in self.attributes[attrib]:
                devdict["attributes"][attrib]["error"] = str(self.attributes[attrib]["error"])
            devdict["attributes"][attrib]["type"] = str(self.attributes[attrib]["type"])
            devdict["attributes"][attrib]["data_format"] = str(
                self.attributes[attrib]["data_format"]
            )
            if self.attributes[attrib]["config"] is not None:
                devdict["attributes"][attrib]["description"] = self.attributes[attrib][
                    "config"
                ].description
                devdict["attributes"][attrib]["root_attr_name"] = self.attributes[attrib][
                    "config"
                ].root_attr_name
                devdict["attributes"][attrib]["format"] = self.attributes[attrib]["config"].format
                devdict["attributes"][attrib]["data_format"] = str(
                    self.attributes[attrib]["config"].data_format
                )
                devdict["attributes"][attrib]["disp_level"] = str(
                    self.attributes[attrib]["config"].disp_level
                )
                devdict["attributes"][attrib]["data_type"] = str(
                    self.attributes[attrib]["config"].data_type
                )
                devdict["attributes"][attrib]["display_unit"] = self.attributes[attrib][
                    "config"
                ].display_unit
                devdict["attributes"][attrib]["standard_unit"] = self.attributes[attrib][
                    "config"
                ].standard_unit
                devdict["attributes"][attrib]["writable"] = str(
                    self.attributes[attrib]["config"].writable
                )
                devdict["attributes"][attrib]["writable_attr_name"] = self.attributes[attrib][
                    "config"
                ].writable_attr_name

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
                devdict["properties"][prop]["type"] = str(type(prop_val))
                # pylint: disable-next=c-extension-no-member
                if type(prop_val) is tango._tango.StdStringVector:
                    devdict["properties"][prop]["value"] = delimiter.join(prop_val)
                else:
                    devdict["properties"][prop]["value"] = prop_val

        self.read_config()

        devdict: dict = {}
        devdict["name"] = self.dev_name
        devdict["version"] = self.version
        devdict["versioninfo"] = self.dev.getversioninfo()
        devdict["adminMode"] = str(self.dev.adminMode).split(".")[1]
        devdict["info"] = {}
        devdict["info"]["dev_class"] = self.info.dev_class
        devdict["info"]["server_host"] = self.info.server_host
        devdict["info"]["server_id"] = self.info.server_id
        devdict["attributes"] = {}
        if self.attribs_found:
            for attrib in self.attribs_found:
                self.logger.debug("Set attribute %s", attrib)
                set_json_attribute()
        else:
            for attrib in self.attributes:
                self.logger.debug("Set attribute %s", attrib)
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

    def read_attribute_value(self) -> None:
        """Read device attributes."""
        for attrib in self.attributes:
            err_msg = None
            attrib_data = None
            try:
                attrib_data = self.dev.read_attribute(attrib)
            except tango.DevFailed as terr:
                # attrib_data = None
                err_msg = str(terr.args[-1].desc)
                self.logger.info("Failed on attribute %s : %s", attrib, err_msg)
                self.attributes[attrib]["error"] = "<ERROR> " + err_msg
                self.attributes[attrib]["type"] = "N/A"
                self.attributes[attrib]["data_format"] = "N/A"
                continue
            self.attributes[attrib]["value"] = attrib_data.value
            self.attributes[attrib]["type"] = str(attrib_data.type)
            self.attributes[attrib]["data_format"] = str(attrib_data.data_format)
            self.logger.info("Read attribute %s : %s", attrib, self.attributes[attrib]["value"])

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
