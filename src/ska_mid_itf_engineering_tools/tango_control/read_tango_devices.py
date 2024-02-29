"""Read and display Tango stuff."""
import json
import logging
import os
import re
import sys
from typing import Any

import tango

from ska_mid_itf_engineering_tools.tango_control.read_tango_device import (
    TangoctlDevice,
    TangoctlDeviceBasic,
)

def md_format(inp: str) -> str:
    """
    Change string to safe format.

    :param inp: input
    :return: output
    """
    outp = inp.replace("/", "\\/").replace("_", "\\_").replace("-", "\\-")
    return outp


def progress_bar(
    iterable: list | dict,
    show: bool,
    prefix: str = '',
    suffix: str = '',
    decimals: int = 1,
    length: int = 100,
    fill: str = '█',
    print_end: str = "\r",
):
    """
    Call this in a loop to create a terminal progress bar.

    :param iterable: Required - iterable object (Iterable)
    :param quiet: suppress output
    :param prefix: Optional - prefix string
    :param suffix: Optional - suffix string
    :param decimals: Optional - positive number of decimals in percent complete
    :param length: Optional - character length of bar
    :param fill: Optional - bar fill character
    :param print_end: Optional - end character (e.g. "\r", "\r\n")
    """

    def print_progress_bar (iteration: Any):
        """
        Progress bar printing function.

        :param iteration: the thing
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = print_end)

    if show:
        # Initial call
        total = len(iterable)
        print_progress_bar(0)
        # Update progress bar
        for i, item in enumerate(iterable):
            yield item
            print_progress_bar(i + 1)
        # Erase line upon completion
        sys.stdout.write("\033[K")
    else:
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
        fmt: str = "json",
    ):
        """
        Read list of Tango devices.

        :param logger: logging handle
        :param evrythng: read and display the whole thing
        :param cfg_data: configuration data
        :param fmt: output format
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

        prog_bar: bool = True
        if fmt == "md":
            prog_bar = False
        if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
            prog_bar = False
        for device in progress_bar(
            device_list, prog_bar, prefix='Devices :', suffix='complete', decimals=0, length=100
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
            new_dev = TangoctlDeviceBasic(logger, device)
            self.devices[device] = new_dev

    def read_config(self) -> None:
        """Read additional data."""
        self.logger.info("Read %d devices", len(self.devices))
        # for device in self.devices:
        for device in progress_bar(
            self.devices, True, prefix='Config  :', suffix='complete', decimals=0, length=100
        ):
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
        tango_port: int,
        fmt: str = "json",
    ):
        """
        Get a dict of devices.

        :param logger: logging handle
        :param cfg_data: configuration data in JSON format
        :param evrythng: get commands and attributes regadrless of state
        :param tgo_name: filter device name
        :param tgo_attrib: filter attribute name
        :param tgo_cmd: filter command name
        :param tgo_prop: filter property name
        :param tango_port: device port
        :param fmt: output format
        :raises Exception: when database connect fails
        """
        self.logger = logger
        self.logger.info(
            "Devices %s : attribute %s command %s property %s",
            tgo_name,
            tgo_attrib,
            tgo_cmd,
            tgo_prop,
        )
        # Get Tango database host
        tango_host = os.getenv("TANGO_HOST")

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
            if fmt == "md":
                prog_bar = False
            if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
                prog_bar = False
            for device in progress_bar(
                device_list, prog_bar, prefix='Devices:', suffix='Complete', length=100
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

    def print_txt_quick(self, devsdict: dict) -> None:
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

        for device in devsdict:
            devdict = devsdict[device]
            print(f"{'name':20} {devdict['name']}")
            print(f"{'version':20} {devdict['version']}")
            print(f"{'versioninfo':20} {devdict['versioninfo'][0]}")
            print(f"{'adminMode':20} {devdict['adminMode']}")
            print_attributes()
            print()

    def print_markdown_all(self, devsdict: dict):
        """Print the whole thing."""

        def print_attribute_data(dstr, dc1, dc2, dc3):
            dc3a = (dc3 / 2) - 3
            dc3b = (dc3 / 2)
            dc4a = (dc3 / 3) - 3
            dc4b = (dc3 / 3) - 2
            dc4c = (dc3 / 3)
            dstr = re.sub(' +', ' ', dstr)
            if dstr[0] == "{" and dstr[-1] == "}":
                ddict = json.loads(dstr)
                self.logger.debug("Print JSON :\n%s", json.dumps(ddict, indent=4))
                n = 0
                for ditem in ddict:
                    if n:
                        print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="")
                    if type(ddict[ditem]) is dict:
                        m = 0
                        for ditem2 in ddict[ditem]:
                            if m:
                                print(f"| {' ':{dc1}}-| {' ':{dc2}}-", end="")
                            print(f"| {ditem} | {ditem2} | {ddict[ditem][ditem2]} |")
                            m += 1
                    elif type(ddict[ditem]) is list:
                        m = 0
                        for ditem2 in ddict[ditem]:
                            dname = f"{ditem} {m}"
                            if not m:
                                print(f"| {dname} ", end="")
                            else:
                                print(f"| {' ':{dc1}},| {' ':{dc2}},| {dname} ", end="")
                            if type(ditem2) is dict:
                                p = 0
                                for ditem3 in ditem2:
                                    if p:
                                        print(f"| {' ':{dc1}},| {' ':{dc2}},| ,", end="")
                                    print(f"| {ditem3} | {ditem2[ditem3]} |")
                                    p += 1
                            else:
                                print(f"| {str(ditem2)} |")
                            m += 1
                    else:
                        print(f"| {ditem} | {str(ddict[ditem])} |")
                    n += 1
            elif "\n" in dstr:
                self.logger.debug("Print '%s'", dstr)
                n = 0
                for line in dstr.split("\n"):
                    line = line.strip()
                    if line:
                        if n:
                            print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="")
                        print(f"| {line:{dc3}} |")
                        n += 1
            else:
                print(f"| {md_format(dstr):{dc3}} |")
            return

        def print_data(dstr, dc1, dc2, dc3):
            if "\n" in dstr:
                self.logger.debug("Print '%s'", dstr)
                n = 0
                for line in dstr.split("\n"):
                    line = line.strip()
                    if line:
                        if n:
                            print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="")
                        print(f"| {line:{dc3}} |")
                        n += 1
            elif len(dstr) > dc3 and "," in dstr:
                n = 0
                for line in dstr.split(","):
                    if n:
                        if dc2:
                            print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="")
                        else:
                            print(f"| {' ':{dc1}}.", end="")
                    print(f"| {line:{dc3}} |")
                    n += 1
            else:
                print(f"| {md_format(dstr):{dc3}} |")

        def print_md_attributes():
            ac1 = 30
            ac2 = 50
            ac3 = 90
            print(f"### Attributes\n")
            n = 0
            print(f"| {'NAME':{ac1}} | {'FIELD':{ac2}} | {'VALUE':{ac3}} |")
            print(f"|:{'-'*ac1}-|:{'-'*ac2}-|:{'-'*ac3}-|")
            for attrib in devdict["attributes"]:
                if n:
                    print(f"| {' '*ac1} ", end="")
                else:
                    print(f"| {md_format(attrib):{ac1}} ", end="")
                m = 0
                self.logger.debug(
                    "Print (%d) attribute %s : %s", m, attrib, devdict["attributes"][attrib]
                )
                for item in devdict["attributes"][attrib]["data"]:
                    data = devdict["attributes"][attrib]["data"][item]
                    if m:
                        print(f"| {' '*ac1} ", end="")
                    print(f"| {md_format(item):{ac2}} ", end="")
                    print_attribute_data(data, ac1, ac2, ac3)
                    m += 1
                for item in devdict["attributes"][attrib]["config"]:
                    config = devdict['attributes'][attrib]['config'][item]
                    print(f"| {' '*ac1} | {md_format(item):{ac2}} ", end="")
                    print_attribute_data(config, ac1, ac2, ac3)
            print("\n")

        def print_md_commands():
            cc1 = 30
            cc2 = 50
            cc3 = 90
            print(f"### Commands\n")
            n = 0
            print(f"| {'NAME':{cc1}} | {'FIELD':{cc2}} | {'VALUE':{cc3}} |")
            print(f"|:{'-'*cc1}-|:{'-'*cc2}-|:{'-'*cc3}-|")
            n = 0
            for cmd in devdict["commands"]:
                print(f"| {cmd:{cc1}} ", end="")
                m = 0
                cmd_items = devdict['commands'][cmd]
                self.logger.debug("Print command %s : %s", cmd, cmd_items)
                for item in cmd_items:
                    if m:
                        print(f"| {' ':{cc1}} ", end="")
                    print(f"| {md_format(item):{cc2}} ", end="")
                    print_data(devdict['commands'][cmd][item], cc1, cc2, cc3)
                    m += 1
                n += 1
            print("\n")

        def print_md_properties():
            pc1 = 40
            pc2 = 133
            print(f"### Properties\n")
            n = 0
            print(f"| {'NAME':{pc1}} | {'VALUE':{pc2}} |")
            print(f"|:{'-'*pc1}-|:{'-'*pc2}-|")
            for prop in devdict["properties"]:
                self.logger.debug("Print command %s : %s", prop, devdict['properties'][prop]['value'])
                print(f"| {md_format(prop):{pc1}} ", end="")
                print_data(devdict['properties'][prop]['value'], pc1, 0, pc2)
            print("\n")

        print("# Tango devices in namespace\n")
        for device in devsdict:
            self.logger.info("Print device %s", device)
            devdict = devsdict[device]
            print(f"## Device {md_format(devdict['name'])}\n")
            print("| FIELD | VALUE |")
            print("|:------|:------|")
            print(f"| version | {devdict['version']} |")
            print(f"| Version info | {devdict['versioninfo'][0]} |")
            print(f"| Admin mode | {devdict['adminMode']} |")
            if "info" in devdict:
                print(f"| Device class | {devdict['info']['dev_class']} |")
                print(f"| Server host | {devdict['info']['server_host']} |")
                print(f"| Server ID | {md_format(devdict['info']['server_id'])} |")
            print("\n")
            print_md_attributes()
            print_md_commands()
            print_md_properties()
            print("\n")

    def print_txt_all(self, devsdict: dict) -> None:  # noqa: C901
        """Print the whole thing."""

        def print_txt(stuff: str) -> None:
            """
            Print attribute, command or property.

            :param stuff: name of the thing
            """
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
                    devkeyval = devkeys[devkey]
                    if type(devkeyval) is dict:
                        # Read dictionary value
                        for devkey2 in devkeyval:
                            devkeyval2 = devkeyval[devkey2]
                            if not j:
                                print(f"{devkey2:40} ", end="")
                            else:
                                print(f"{' ':61} {devkey2:40} ", end="")
                            j += 1
                            if not devkeyval2:
                                print()
                            elif "\n" in devkeyval2:
                                keyvals = devkeyval2.split("\n")
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
                            elif "," in devkeyval2:
                                keyvals = devkeyval2.split(",")
                                keyval = keyvals[0]
                                print(f"{keyval}")
                                for keyval in keyvals[1:]:
                                    print(f"{' ':102} {keyval}")
                            else:
                                keyvals2 = []
                                if len(devkeyval2) > 70:
                                    lsp = devkeyval2[0:70].rfind(" ")
                                    keyvals2.append(devkeyval2[0:lsp])
                                    keyvals2.append(devkeyval2[lsp + 1 :])
                                else:
                                    keyvals2.append(" ".join(devkeyval2.split()))
                                print(f"{keyvals2[0]}")
                                for keyval2 in keyvals2[1:]:
                                    print(f"{' ':102} {keyval2}")
                    else:
                        # Read string value
                        if not j:
                            print(f"{devkey:40} ", end="")
                        else:
                            print(f"{' ':61} {devkey:40} ", end="")
                        j += 1
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
                            print(f"{keyvals2[0]}")
                            for keyval2 in keyvals2[1:]:
                                print(f"{' ':102} {keyval2}")

        for device in devsdict:
            self.logger.info("Print device %s", device)
            devdict = devsdict[device]
            print(f"{'name':20} {devdict['name']}")
            print(f"{'version':20} {devdict['version']}")
            print(f"{'versioninfo':20} {devdict['versioninfo'][0]}")
            print(f"{'adminMode':20} {devdict['adminMode']}")
            if "info" in devdict:
                print(f"{' ':20} {'info':40} {'dev_class':40} {devdict['info']['dev_class']}")
                print(f"{' ':20} {' ':40} {'server_host':40} {devdict['info']['server_host']}")
                print(f"{' ':20} {' ':40} {'server_id':40} {devdict['info']['server_id']}")
            print_txt("attributes")
            print_txt("commands")
            print_txt("properties")
            print()

    def print_txt(self, disp_action: int) -> None:
        """
        Print in text format.

        :param disp_action: display control flag
        """
        if disp_action == 4:
            self.print_txt_list()
        elif disp_action == 3:
            devsdict = self.get_json()
            self.print_txt_quick(devsdict)
        else:
            devsdict = self.get_json()
            self.print_txt_all(devsdict)

    def print_json(self, disp_action: int) -> None:
        """
        Print in JSON format.

        :param disp_action: display control flag
        """
        devsdict = self.get_json()
        print(json.dumps(devsdict, indent=4))

    def print_markdown(self, disp_action: int) -> None:
        """
        Print in JSON format.

        :param disp_action: display control flag
        """
        devsdict = self.get_json()
        self.print_markdown_all(devsdict)
