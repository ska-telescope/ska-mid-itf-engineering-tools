"""Read and display Tango stuff."""
import json
import logging
import os
from typing import Any

import tango


class TangoctlDevice:
    """Compile a dictionary for a Tango device."""

    logger: logging.Logger
    dev: tango.DeviceProxy
    commands: dict = {}
    attributes: dict = {}
    properties: dict = {}
    command_config: Any

    def __init__(self, logger: logging.Logger, device: str):
        self.logger = logger
        self.logger.info("Add device %s", device)
        self.dev = tango.DeviceProxy(device)
        self.dev_name = self.dev.name()
        cmds = sorted(self.dev.get_command_list())
        for cmd in cmds:
            self.logger.debug("Add command %s", cmd)
            self.commands[cmd] = {}
            self.commands[cmd]["config"] = self.dev.get_command_config(cmd)
        attribs = sorted(self.dev.get_attribute_list())
        for attrib in attribs:
            self.logger.debug("Add attribute %s", attrib)
            self.attributes[attrib] = {}
            self.attributes[attrib]["config"] = self.dev.get_attribute_config(attrib)
        props = sorted(self.dev.get_property_list("*"))
        for prop in props:
            self.logger.debug("Add property %s", prop)
            self.properties[prop] = {}
        self.info = self.dev.info()
        self.version = self.dev.versionId

    def get_commands(self) -> dict:
        return self.commands

    def get_attributes(self) -> dict:
        return self.attributes

    def get_properties(self) -> dict:
        return self.properties

    # def get_info(self):
    #     return self.attributes, self.commands, self.properties

    def get_json(self, delimiter: str) -> dict:  # noqa: C901
        """Convert internal values to JSON."""

        def set_json_attribute() -> None:
            devdict["attributes"][attrib] = {}
            if "value" in self.attributes[attrib]:
                devdict["attributes"][attrib]["value"] = str(self.attributes[attrib]["value"])
            if "error" in self.attributes[attrib]:
                devdict["attributes"][attrib]["error"] = str(self.attributes[attrib]["error"])
            devdict["attributes"][attrib]["type"] = str(self.attributes[attrib]["type"])
            devdict["attributes"][attrib]["data_format"] = str(
                self.attributes[attrib]["data_format"]
            )
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
            devdict["commands"][cmd] = {}
            devdict["commands"][cmd]["in_type"] = repr(self.commands[cmd]["config"].in_type)
            devdict["commands"][cmd]["in_type_desc"] = self.commands[cmd]["config"].in_type_desc
            devdict["commands"][cmd]["out_type"] = repr(self.commands[cmd]["config"].out_type)
            devdict["commands"][cmd]["out_type_desc"] = self.commands[cmd]["config"].out_type_desc

        def set_json_property() -> None:
            if "value" in self.properties[prop]:
                prop_val = self.properties[prop]["value"]
                devdict["properties"][prop] = {}
                devdict["properties"][prop]["type"] = str(type(prop_val))
                if type(prop_val) is tango._tango.StdStringVector:
                    devdict["properties"][prop]["value"] = delimiter.join(prop_val)
                else:
                    devdict["properties"][prop]["value"] = prop_val

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
        for prop in self.properties:
            self.properties[prop]["value"] = self.dev.get_property(prop)[prop]
            self.logger.debug("Read property %s : %s", prop, self.properties[prop]["value"])
        return


class TangoctlDevices:
    """Compile a dictionary of available Tango devices."""

    devices: dict = {}

    def __init__(
        self,
        logger: logging.Logger,
        evrythng: bool,
        cfg_data: dict,
        itype: str | None,
    ):
        """
        Get a dict of devices.

        :param logger: logging handle
        :param cfg_data: configuration data in JSON format
        :param evrythng: get commands and attributes regadrless of state
        :param itype: filter device name
        :return: list of devices
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
            if itype:
                iupp = device.upper()
                if itype not in iupp:
                    self.logger.info(f"Ignore {device}")
                    continue
            logger.debug("Add device %s", device)
            self.devices[device] = TangoctlDevice(logger, device)
        logger.debug("Read %d devices", len(self.devices))

    def read_attribute_values(self) -> None:
        for device in self.devices:
            self.devices[device].read_attribute_value()

    def read_command_values(self) -> None:
        for device in self.devices:
            self.devices[device].read_command_value(self.run_commands, self.run_commands_name)

    def read_property_values(self) -> None:
        for device in self.devices:
            self.devices[device].read_property_value()

    def read_device_values(self) -> None:
        self.read_attribute_values()
        # self.read_command_values()
        self.read_property_values()

    def print_device_values(self) -> None:
        for device in self.devices:
            dev = self.devices[device]
            self.logger.info("ATTRIBUTES: %s", dev.get_attributes())
            self.logger.info("COMMANDS: %s", dev.get_commands())
            self.logger.info("PROPERTIES: %s", dev.get_properties())

    def get_devices(self) -> dict:
        """
        Get list of devices.

        :return: list of devices
        """
        return self.devices

    def list_devices(self) -> None:
        for device in self.devices:
            print(device)

    def get_json(self) -> dict:
        devsdict = {}
        for device in self.devices:
            devsdict[device] = self.devices[device].get_json(self.delimiter)
        return devsdict

    # def print_txt(self):
    #     devsdict = self.get_json()
    #     for device in devsdict:
    #         i = 0
    #         for heading1 in devsdict[device]:
    #             print(f"{heading1:20}", end="")
    #             i += 1
    #             heading1_vals = devsdict[device][heading1]
    #             if type(heading1_vals) is dict:
    #                 j = 0
    #                 for key1 in heading1_vals:
    #                     if not j:
    #                         print(f" {key1:40}", end="")
    #                     else:
    #                         print(f" {' ':40}", end="")
    #                     j += 1
    #                     heading2_vals = heading1_vals[key1]
    #                     if type(heading2_vals) is dict:
    #                         k = 0
    #                         for key2 in heading2_vals:
    #                             if not k:
    #                                 print(f" {key2:20} {heading2_vals[key2]}")
    #                             else:
    #                                 print(f"{' ':81} {key2:20} {heading2_vals[key2]}")
    #                             k += 1
    #                     else:
    #                         print(f"{' ':81} {heading2_vals}")
    #                 print()
    #             else:
    #                 print(heading1_vals)

    def print_txt(self) -> None:  # noqa: C901
        # def print_attributes():
        #     print(f"{'attributes':20}", end="")
        #     i = 0
        #     for attrib in devdict["attributes"]:
        #         if not i:
        #             print(f" {attrib:40}", end="")
        #         else:
        #             print(f" {' ':20} {attrib:40}", end="")
        #         i += 1
        #         devattribs = devdict["attributes"][attrib]
        #         j = 0
        #         for devattrib in devattribs:
        #             if not j:
        #                 print(f" {devattrib:40}", end="")
        #             else:
        #                 print(f" {' ':61} {devattrib:40}", end="")
        #             j += 1
        #             devattribval = devattribs[devattrib]
        #             if "\n" in devattribval:
        #                 attribvals = devattribval.split("\n")
        #                 # Remove empty lines
        #                 attribvals2 = []
        #                 for attribval in attribvals:
        #                     attribval2 = attribval.strip()
        #                     if attribval2:
        #                         attribvals2.append(attribval2)
        #                 attribval2 = attribvals2[0]
        #                 print(f" {attribval2}")
        #                 for attribval2 in attribvals2[1:]:
        #                     print(f" {' ':102} {attribval2}")
        #             else:
        #                 print(f" {devattribval}")

        def print_stuff(stuff: str) -> None:
            print(f"{stuff:20} ", end="")
            i = 0
            for key in devdict[stuff]:
                if not i:
                    print(f"{key:40} ", end="")
                else:
                    print(f"{' ':20} {key:40} ", end="")
                i += 1
                devkeys = devdict[stuff][key]
                j = 0
                for devkey in devkeys:
                    if not j:
                        print(f"{devkey:40} ", end="")
                    else:
                        print(f"{' ':61} {devkey:40} ", end="")
                    j += 1
                    devkeyval = devkeys[devkey]
                    if "\n" in devkeyval:
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

    def print_json(self) -> None:
        devsdict = self.get_json()
        print(json.dumps(devsdict, indent=4))
