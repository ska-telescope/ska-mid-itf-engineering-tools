"""Read and display Tango stuff."""
import json
import logging
import os
from typing import Any

import tango


class TangoctlDeviceBasic:
    """Compile a basic dictionary for a Tango device."""

    logger: logging.Logger
    dev: tango.DeviceProxy

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
        self.logger.debug("Add device %s with attribute %s", device)
        self.dev = tango.DeviceProxy(device)
        self.dev_name = self.dev.name()


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
        self.info = self.dev.info()
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
                self.commands[cmd]["value"] = self.dev.command_inout()
                self.logger.debug(
                    "Read command %s (%s) : %s",
                    cmd,
                    type(self.commands[cmd]["value"]),
                    self.commands[cmd]["value"],
                )
            elif cmd in run_commands_name:
                self.commands[cmd]["value"] = self.dev.command_inout(self.dev_name)
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


class TangoctlDevices:
    """Compile a dictionary of available Tango devices."""

    devices: dict = {}
    attribs_found: list = []

    def __init__(  # noqa: C901s
        self,
        logger: logging.Logger,
        evrythng: bool,
        cfg_data: dict,
        tgo_name: str | None,
        tgo_attrib: str | None,
        tgo_cmd: str | None,
        tgo_prop: str | None,
    ):
        """
        Get a dict of devices.

        :param logger: logging handle
        :param cfg_data: configuration data in JSON format
        :param evrythng: get commands and attributes regadrless of state
        :param tgo_name: filter device name
        :param tgo_name: filter attribute name
        :param tgo_cmd: filter command name
        :param tgo_prop: filter property name
        """
        self.logger = logger
        # Get Tango database host
        tango_host = os.getenv("TANGO_HOST")

        self.delimiter = cfg_data["delimiter"]
        self.run_commands = cfg_data["run_commands"]
        self.logger.info("Run commands %s", self.run_commands)
        self.run_commands_name = cfg_data["run_commands_name"]
        self.logger.info("Run commands with name %s", self.run_commands_name)

        # Connect to database
        try:
            database = tango.Database()
        except Exception as terr:
            self.logger.error("Could not connect to Tango database %s", tango_host)
            raise terr

        # Read devices
        device_list = database.get_device_exported("*")
        logger.info(f"{len(device_list)} devices available")

        for device in sorted(device_list.value_string):
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
                iupp = device.upper()
                if tgo_name not in iupp:
                    self.logger.info(f"Ignore {device}")
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
                logger.debug("Add device %s", device)
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
        # self.read_command_values()
        self.read_property_values()

    def get_json(self) -> dict:
        """
        Read device data.

        :return: dictionary
        """
        devsdict = {}
        for device in self.devices:
            devsdict[device] = self.devices[device].get_json(self.delimiter)
        return devsdict

    def print_txt_quick(self) -> None:
        """Print text in short form."""

        def print_attributes() -> None:
            """Print attribute in short form."""
            print(f"{'attributes':20}", end="")
            i = 0
            for attrib in devdict["attributes"]:
                if not i:
                    print(f" {attrib:40}", end="")
                else:
                    print(f" {' ':20} {attrib:40}", end="")
                i += 1
                print(f"{devdict['attributes'][attrib]['value']}")

        devsdict = self.get_json()
        for device in devsdict:
            devdict = devsdict[device]
            print(f"{'name':20} {devdict['name']}")
            print(f"{'version':20} {devdict['version']}")
            print(f"{'versioninfo':20} {devdict['versioninfo'][0]}")
            print(f"{'adminMode':20} {devdict['adminMode']}")
            print_attributes()
            print()

    def print_txt_all(self) -> None:  # noqa: C901
        """Print the whole thing."""

        def print_stuff(stuff: str) -> None:
            """Print attribute, command or property."""
            self.logger.debug("Print %d %s", len(devdict[stuff]), stuff)
            if not devdict[stuff]:
                return
            print(f"{stuff:20} ", end="")
            if not devdict[stuff]:
                print()
                return
            i = 0
            for key in devdict[stuff]:
                if not i:
                    print(f"{key:40} ", end="")
                else:
                    print(f"{' ':20} {key:40} ", end="")
                i += 1
                devkeys = devdict[stuff][key]
                if not devkeys:
                    print()
                    continue
                j = 0
                for devkey in devkeys:
                    if not j:
                        print(f"{devkey:40} ", end="")
                    else:
                        print(f"{' ':61} {devkey:40} ", end="")
                    j += 1
                    devkeyval = devkeys[devkey]
                    if not devkeyval:
                        print()
                    elif "\n" in devkeyval:
                        keyvals = devkeyval.split("\n")
                        # Remove empty lines
                        keyvals2 = []
                        for keyval in keyvals:
                            keyval2 = keyval.strip()
                            if keyval2:
                                if len(keyval2) > 70:
                                    lsp = keyval2[0:70].rfind(" ")
                                    keyvals2.append(keyval2[0:lsp])
                                    keyvals2.append(keyval2[lsp + 1 :])
                                else:
                                    keyvals2.append(" ".join(keyval2.split()))
                        print(f"{keyvals2[0]}")
                        for keyval2 in keyvals2[1:]:
                            print(f"{' ':102} {keyval2}")
                    elif "," in devkeyval:
                        keyvals = devkeyval.split(",")
                        keyval = keyvals[0]
                        print(f"{keyval}")
                        for keyval in keyvals[1:]:
                            print(f"{' ':102} {keyval}")
                    else:
                        keyvals2 = []
                        if len(devkeyval) > 70:
                            lsp = devkeyval[0:70].rfind(" ")
                            keyvals2.append(devkeyval[0:lsp])
                            keyvals2.append(devkeyval[lsp + 1 :])
                        else:
                            keyvals2.append(" ".join(devkeyval.split()))
                        # print(f"{' '.join(devkeyval.split())}")
                        print(f"{keyvals2[0]}")
                        for keyval2 in keyvals2[1:]:
                            print(f"{' ':102} {keyval2}")

        devsdict = self.get_json()
        for device in devsdict:
            self.logger.info("Print device %s", device)
            devdict = devsdict[device]
            print(f"{'name':20} {devdict['name']}")
            print(f"{'version':20} {devdict['version']}")
            print(f"{'versioninfo':20} {devdict['versioninfo'][0]}")
            print(f"{'adminMode':20} {devdict['adminMode']}")
            print(f"{' ':20} {'info':40} {'dev_class':40} {devdict['info']['dev_class']}")
            print(f"{' ':20} {' ':40} {'server_host':40} {devdict['info']['server_host']}")
            print(f"{' ':20} {' ':40} {'server_id':40} {devdict['info']['server_id']}")
            # print_attributes()
            print_stuff("attributes")
            print_stuff("commands")
            print_stuff("properties")
            print()

    def print_txt(self, disp_action: int) -> None:
        """
        Print in text format.

        :param disp_action: display control flag
        """
        if disp_action == 3:
            self.print_txt_quick()
        else:
            self.print_txt_all()

    def print_json(self, disp_action: int) -> None:
        """
        Print in JSON format.

        :param disp_action: display control flag
        """
        devsdict = self.get_json()
        print(json.dumps(devsdict, indent=4))
