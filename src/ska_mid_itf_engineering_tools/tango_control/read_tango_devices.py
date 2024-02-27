"""Read and display Tango stuff."""
import json
import logging
import os
from typing import Any

import tango

from ska_mid_itf_engineering_tools.tango_control.read_tango_device import (
    TangoctlDevice,
    TangoctlDeviceBasic,
)


class TangoctlDevicesBasic:
    """Compile a dictionary of available Tango devices."""

    devices: dict = {}

    def __init__(  # noqa: C901s
        self,
        logger: logging.Logger,
        evrythng: bool,
        cfg_data: Any,
    ):
        """
        Read list of Tango devices.

        :param logger: logging handle
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
        device_list = database.get_device_exported("*")
        self.logger.info(f"{len(device_list)} devices available")

        for device in sorted(device_list.value_string):
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
            new_dev = TangoctlDeviceBasic(logger, device)
            self.devices[device] = new_dev

    def read_config(self) -> None:
        """Read additional data."""
        self.logger.info("Read %d devices", len(self.devices))
        for device in self.devices:
            self.devices[device].read_config()

    def print_txt_list(self) -> None:
        """Print list of devices."""
        self.logger.info("List %d devices", len(self.devices))
        print(f"{'DEVICE NAME':40} {'STATE':10} {'ADMIN':11} {'VERSION':8} CLASS")
        for device in self.devices:
            # print(f"{device}")
            self.devices[device].print_list()


class TangoctlDevices(TangoctlDevicesBasic):
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
        self.logger.info(f"{len(device_list)} devices available")

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

    def print_txt_list(self) -> None:
        """Print list of devices."""
        self.logger.info("List %d devices", len(self.devices))
        for device in self.devices:
            print(f"{device}")

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
        if disp_action == 4:
            self.print_txt_list()
        elif disp_action == 3:
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
