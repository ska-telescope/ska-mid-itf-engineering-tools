"""Read and display Tango stuff."""

import ast
import json
import logging
import os
import re
import sys
from typing import Any, TextIO
from ska_mid_itf_engineering_tools.tango_control.read_tango_device import progress_bar


def md_format(inp: str) -> str:
    """
    Change string to safe format.

    :param inp: input
    :return: output
    """
    if type(inp) is not str:
        return str(inp)
    outp = inp.replace("/", "\\/").replace("_", "\\_").replace("-", "\\-")
    return outp


def md_print(inp: str, end: str = "\n", file: TextIO = sys.stdout) -> None:
    """
    Print markdown string.

    :param inp: input
    :param end: at the end of the line
    :param file: output file pointer
    """
    print(inp.replace("_", "\\_").replace("-", "\\-"), end=end, file=file)


class BooleanEncoder(json.JSONEncoder):
    """Using a custom encoder"""
    def default(self, o: Any) -> Any:
        """
        This is the default handler.

        :param o: object
        :return: the thing
        """
        if isinstance(o, bool):
            return str(o).lower()
        return super().default(o)


class TangoJsonReader:
    """Read JSON and print as markdown or text."""

    outf: TextIO
    tgo_space: str

    def __init__(
        self,
        logger: logging.Logger,
        kube_namespace: str | None,
        devsdict: dict,
        file_name: str | None = None,
    ):
        """
        Rock and roll.

        :param logger: logging handle
        :param kube_namespace: Kubernetes namespace
        :param devsdict: dictionary with device data
        :param file_name: output file name
        """
        self.logger = logger
        self.devices_dict = devsdict
        if file_name is not None:
            self.logger.info("Write file %s", file_name)
            self.outf = open(file_name, "w")
        else:
            self.outf = sys.stdout
        # Get Tango database host
        tango_host = os.getenv("TANGO_HOST")
        if kube_namespace is not None:
            self.tgo_space = f"namespace {kube_namespace}"
        else:
            self.tgo_space = f"host {tango_host}"
        self.prog_bar: bool = True
        if self.logger.getEffectiveLevel() in (logging.DEBUG, logging.INFO):
            self.prog_bar = False

    def print_markdown_all(self) -> None:  # noqa: C901
        """Print the whole thing."""

        def print_attribute_data(item: str, dstr: str) -> None:
            """
            Print attribute data in various formats.

            :param item: item name
            :param dstr: itmen value
            """
            dstr = re.sub(" +", " ", dstr)
            md_print(f"| {item:30} ", end="", file=self.outf)
            if not dstr:
                print(f"| {' ':143} ||", file=self.outf)
            elif dstr[0] == "{" and dstr[-1] == "}":
                if "'" in dstr:
                    dstr = dstr.replace("'", "\"")
                try:
                    # ddict = json.loads(dstr, cls=BooleanEncoder)
                    ddict = json.loads(dstr)
                except json.decoder.JSONDecodeError as jerr:
                    # TODO this string breaks it
                    # {
                    # "state": "DevState.ON", "healthState": "HealthState.OK", "ping": "545",
                    # "last_event_arrived": "1709799240.7604482", "unresponsive": "False",
                    # "exception": "", "isSubarrayAvailable": True, "resources": [],
                    # "device_id ": -1, "obsState": "ObsState.EMPTY"
                    # }
                    self.logger.info("Error : %s", str(jerr))
                    self.logger.info("Could not read : %s", dstr)
                    # print(f"| <ERROR> {str(jerr):134} ||")
                    print(f"| {dstr:143} ||", file=self.outf)
                    return
                self.logger.debug("Print JSON :\n%s", json.dumps(ddict, indent=4))
                n = 0
                for ditem in ddict:
                    if n:
                        print(f"| {' ':30} ", end="", file=self.outf)
                    if type(ddict[ditem]) is dict:
                        m = 0
                        for ditem2 in ddict[ditem]:
                            md_print(
                                f"| {ditem:{50}} | {ditem2:42} | {ddict[ditem][ditem2]:45} |",
                                file=self.outf,
                            )
                            m += 1
                    elif type(ddict[ditem]) is list or type(ddict[ditem]) is tuple:
                        m = 0
                        for ditem2 in ddict[ditem]:
                            self.logger.debug(
                                "Print attribute value list item %s (%s)", ditem2, type(ditem2)
                            )
                            dname = f"{ditem} {m}"
                            if not m:
                                md_print(f"| {dname:90} ", end="", file=self.outf)
                            else:
                                md_print(
                                    f"| {' ':30} | {' ':50} | {dname:90} ", end="", file=self.outf
                                )
                            md_print(f"| {dname:50} ", end="", file=self.outf)
                            if type(ditem2) is dict:
                                p = 0
                                for ditem3 in ditem2:
                                    md_print(
                                        f"| {ditem3:42} | {ditem2[ditem3]:45} |", file=self.outf
                                    )
                                    p += 1
                            else:
                                md_print(f"| {ditem2:143}  ||", file=self.outf)
                            m += 1
                    else:
                        md_print(f"| {ditem:50} | {ddict[ditem]:90} ||", file=self.outf)
                    n += 1
            elif dstr[0] == "[" and dstr[-1] == "]":
                dlist = ast.literal_eval(dstr)
                self.logger.debug("Print attribute value list %s (%s)", dlist, type(dlist))
                n = 0
                for ditem in dlist:
                    if n:
                        print(f"| {' ':30} ", end="", file=self.outf)
                    if type(ditem) is dict:
                        m = 0
                        for ditem2 in ditem:
                            ditem_val = str(ditem[ditem2])
                            if m:
                                print(f"| {' ':30} ", end="", file=self.outf)
                            md_print(f"| {ditem2:50} ", end="", file=self.outf)
                            md_print(f"| {ditem_val:90} |", file=self.outf)
                            m += 1
                    else:
                        md_print(f"| {str(ditem):143} ||", file=self.outf)
                    n += 1
            elif "\n" in dstr:
                self.logger.debug("Print attribute value str %s (%s)", dstr, type(dstr))
                n = 0
                for line in dstr.split("\n"):
                    line = line.strip()
                    if line:
                        if n:
                            print(f"| {' ':30} ", end="", file=self.outf)
                        md_print(f"| {line:143} ||", file=self.outf)
                        n += 1
            else:
                if len(dstr) > 140:
                    lsp = dstr[0:140].rfind(" ")
                    md_print(f" | {dstr[0:lsp]:143} ||", file=self.outf)
                    md_print(f"| {' ':30}  | {dstr[lsp + 1 :]:143} ||", file=self.outf)
                else:
                    md_print(f"| {dstr:143} ||", file=self.outf)
            return

        def print_data(dstr: str, dc1: int, dc2: int, dc3: int) -> None:
            """
            Print device data.

            :param dstr: data string
            :param dc1: column 1 width
            :param dc2: column 2 width
            :param dc3: column 2 width
            """
            if not dstr:
                md_print(f"| {' ':{dc3}} |", file=self.outf)
            elif type(dstr) is not str:
                md_print(f"| {str(dstr):{dc3}} |", file=self.outf)
            elif "\n" in dstr:
                self.logger.debug("Print '%s'", dstr)
                n = 0
                for line in dstr.split("\n"):
                    line = line.strip()
                    if line:
                        if n:
                            print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="", file=self.outf)
                        md_print(f"| {line:{dc3}} |", file=self.outf)
                        n += 1
            elif len(dstr) > dc3 and "," in dstr:
                n = 0
                for line in dstr.split(","):
                    if n:
                        if dc2:
                            print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="", file=self.outf)
                        else:
                            print(f"| {' ':{dc1}}.", end="", file=self.outf)
                    md_print(f"| {line:{dc3}} |", file=self.outf)
                    n += 1
            else:
                md_print(f"| {str(dstr):{dc3}} |", file=self.outf)

        def print_md_attributes() -> None:
            """Print attributes."""
            print("### Attributes\n", file=self.outf)
            for attrib in devdict["attributes"]:
                print(f"#### {attrib}\n", file=self.outf)
                print("| ITEM | VALUE |       |", file=self.outf)
                print("|:-----|:------|:------|", file=self.outf)
                attrib_data = devdict["attributes"][attrib]["data"]
                for item in attrib_data:
                    data = attrib_data[item]
                    if type(data) is str:
                        self.logger.debug("Print attribute str %s : %s", item, data)
                        print_attribute_data(item, data)
                    elif type(data) is dict:
                        self.logger.debug("Print attribute dict %s : %s", item, data)
                        n = 0
                        for item2 in data:
                            print_attribute_data(item2, str(data[item2]))
                            n += 1
                    elif type(data) is list:
                        self.logger.debug("Print attribute list %s : %s", item, data)
                        n = 0
                        for item2 in data:
                            if not n:
                                md_print(f"| {item:30} ", end="", file=self.outf)
                            else:
                                print(f"| {' ':30} ", end="", file=self.outf)
                            md_print(f"| {item2:143} ||", file=self.outf)
                            n += 1
                    else:
                        self.logger.warning(
                            "Data type for %s (%s) not supported", item, type(data)
                        )
                if "config" in devdict["attributes"][attrib]:
                    for item in devdict["attributes"][attrib]["config"]:
                        config = devdict["attributes"][attrib]["config"][item]
                        print_attribute_data(item, config)
                print("\n*******\n", file=self.outf)
            print("\n", file=self.outf)

        def print_md_commands() -> None:
            """Print commands."""
            cc1 = 30
            cc2 = 50
            cc3 = 90
            print("### Commands\n", file=self.outf)
            print(f"| {'NAME':{cc1}} | {'FIELD':{cc2}} | {'VALUE':{cc3}} |", file=self.outf)
            print(f"|:{'-'*cc1}-|:{'-'*cc2}-|:{'-'*cc3}-|", file=self.outf)
            n = 0
            for cmd in devdict["commands"]:
                print(f"| {cmd:{cc1}} ", end="", file=self.outf)
                m = 0
                cmd_items = devdict["commands"][cmd]
                self.logger.debug("Print command %s : %s", cmd, cmd_items)
                if cmd_items:
                    for item in cmd_items:
                        if m:
                            print(f"| {' ':{cc1}} ", end="", file=self.outf)
                        md_print(f"| {item:{cc2}} ", end="", file=self.outf)
                        print_data(devdict["commands"][cmd][item], cc1, cc2, cc3)
                        m += 1
                else:
                    md_print(f"| {' ':{cc2}} | {' ':{cc3}} |", file=self.outf)
                n += 1
            print("\n*******\n", file=self.outf)

        def print_md_properties() -> None:
            """Print properties."""
            pc1 = 40
            pc2 = 133
            print("### Properties\n", file=self.outf)
            print(f"| {'NAME':{pc1}} | {'VALUE':{pc2}} |", file=self.outf)
            print(f"|:{'-'*pc1}-|:{'-'*pc2}-|", file=self.outf)
            for prop in devdict["properties"]:
                self.logger.debug(
                    "Print command %s : %s", prop, devdict["properties"][prop]["value"]
                )
                md_print(f"| {prop:{pc1}} ", end="", file=self.outf)
                print_data(devdict["properties"][prop]["value"], pc1, 0, pc2)
            print("\n*******\n", file=self.outf)

        print(f"# Tango devices in {self.tgo_space}\n", file=self.outf)
        # Run "for device in self.devices_dict:"
        for device in progress_bar(
            self.devices_dict,
            self.prog_bar,
            prefix=f"Read {len(self.devices_dict)} JSON devices :",
            suffix="complete",
            decimals=0,
            length=100,
        ):
            self.logger.info("Print device %s", device)
            devdict = self.devices_dict[device]
            md_print(f"## Device {devdict['name']}\n", file=self.outf)
            print("| FIELD | VALUE |", file=self.outf)
            print("|:------|:------|", file=self.outf)
            print(f"| version | {devdict['version']} |", file=self.outf)
            if "versioninfo" in devdict:
                md_print(f"| Version info | {devdict['versioninfo'][0]} |", file=self.outf)
            if "adminMode" in devdict:
                print(f"| Admin mode | {devdict['adminMode']} |", file=self.outf)
            if "info" in devdict:
                md_print(f"| Device class | {devdict['info']['dev_class']} |", file=self.outf)
                md_print(f"| Server host | {devdict['info']['server_host']} |", file=self.outf)
                md_print(f"| Server ID | {devdict['info']['server_id']} |", file=self.outf)
            print("\n*******\n", file=self.outf)
            print_md_attributes()
            print_md_commands()
            print_md_properties()
            print("\n", file=self.outf)

    def print_txt_all(self) -> None:  # noqa: C901
        """Print the whole thing."""

        def print_txt(stuff: str) -> None:
            """
            Print attribute, command or property.

            :param stuff: name of the thing
            """
            self.logger.debug("Print %d %s", len(devdict[stuff]), stuff)
            if not devdict[stuff]:
                return
            print(f"{stuff:20} ", end="", file=self.outf)
            if not devdict[stuff]:
                print(file=self.outf)
                return
            i = 0
            for key in devdict[stuff]:
                if not i:
                    print(f"{key:40} ", end="", file=self.outf)
                else:
                    print(f"{' ':20} {key:40} ", end="", file=self.outf)
                i += 1
                devkeys = devdict[stuff][key]
                if not devkeys:
                    print(file=self.outf)
                    continue
                j = 0
                for devkey in devkeys:
                    devkeyval = devkeys[devkey]
                    if type(devkeyval) is dict:
                        # Read dictionary value
                        for devkey2 in devkeyval:
                            devkeyval2 = devkeyval[devkey2]
                            if not j:
                                print(f"{devkey2:40} ", end="", file=self.outf)
                            else:
                                print(f"{' ':61} {devkey2:40} ", end="", file=self.outf)
                            j += 1
                            if not devkeyval2:
                                print(file=self.outf)
                            elif type(devkeyval2) is list:
                                keyval = devkeyval2[0]
                                print(f"{keyval}", file=self.outf)
                                for keyval in devkeyval2[1:]:
                                    print(f"{' ':102} {keyval}", file=self.outf)
                            elif type(devkeyval2) is dict:
                                n = 0
                                for keyval in devkeyval2:
                                    if n:
                                        print(f"{' ':102} ", end="", file=self.outf)
                                    if type(devkeyval2[keyval]) is list:
                                        m = 0
                                        for item in devkeyval2[keyval][1:]:
                                            if m:
                                                print(f"{' ':102} ", end="", file=self.outf)
                                            print(f"{keyval:24}", end="", file=self.outf)
                                            if type(item) is dict:
                                                k = 0
                                                for key2 in item:
                                                    if k:
                                                        print(
                                                            f"{' ':126} ", end="", file=self.outf
                                                        )
                                                    print(
                                                        f" {key2:32} {item[key2]}", file=self.outf
                                                    )
                                                    k += 1
                                            else:
                                                print(f" {item}", file=self.outf)
                                            m += 1
                                    elif type(devkeyval2[keyval]) is not str:
                                        print(f"{keyval:24} ", end="", file=self.outf)
                                        print(f"{devkeyval2[keyval]}", file=self.outf)
                                    else:
                                        print(
                                            f"{keyval:24} -> {devkeyval2[keyval]}", file=self.outf
                                        )
                                    n += 1
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
                                print(f"{keyvals2[0]}", file=self.outf)
                                for keyval2 in keyvals2[1:]:
                                    print(f"{' ':102} {keyval2}", file=self.outf)
                            elif "," in devkeyval2:
                                keyvals = devkeyval2.split(",")
                                keyval = keyvals[0]
                                print(f"{keyval}", file=self.outf)
                                for keyval in keyvals[1:]:
                                    print(f"{' ':102} {keyval}", file=self.outf)
                            else:
                                keyvals2 = []
                                if len(devkeyval2) > 70:
                                    lsp = devkeyval2[0:70].rfind(" ")
                                    keyvals2.append(devkeyval2[0:lsp])
                                    keyvals2.append(devkeyval2[lsp + 1 :])
                                else:
                                    keyvals2.append(" ".join(devkeyval2.split()))
                                print(f"{keyvals2[0]}", file=self.outf)
                                for keyval2 in keyvals2[1:]:
                                    print(f"{' ':102} {keyval2}", file=self.outf)
                    else:
                        # Read string value
                        if not j:
                            print(f"{devkey:40} ", end="", file=self.outf)
                        else:
                            print(f"{' ':61} {devkey:40} ", end="", file=self.outf)
                        j += 1
                        if not devkeyval:
                            print(file=self.outf)
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
                            print(f"{keyvals2[0]}", file=self.outf)
                            for keyval2 in keyvals2[1:]:
                                print(f"{' ':102} {keyval2}", file=self.outf)
                        elif "," in devkeyval:
                            keyvals = devkeyval.split(",")
                            keyval = keyvals[0]
                            print(f"{keyval}", file=self.outf)
                            for keyval in keyvals[1:]:
                                print(f"{' ':102} {keyval}", file=self.outf)
                        else:
                            keyvals2 = []
                            if type(devkeyval) is list:
                                keyvals2 = devkeyval
                            elif len(devkeyval) > 70:
                                lsp = devkeyval[0:70].rfind(" ")
                                keyvals2.append(devkeyval[0:lsp])
                                keyvals2.append(devkeyval[lsp + 1 :])
                            else:
                                keyvals2.append(" ".join(devkeyval.split()))
                            print(f"{keyvals2[0]}", file=self.outf)
                            for keyval2 in keyvals2[1:]:
                                print(f"{' ':102} {keyval2}", file=self.outf)

        for device in self.devices_dict:
            self.logger.info("Print device %s", device)
            devdict = self.devices_dict[device]
            print(f"{'name':20} {devdict['name']}", file=self.outf)
            print(f"{'version':20} {devdict['version']}", file=self.outf)
            print(f"{'green mode':20} {devdict['green_mode']}", file=self.outf)
            # print(f"{'versioninfo':20} {devdict['versioninfo'][0]}", file=self.outf)
            # print(f"{'adminMode':20} {devdict['adminMode']}", file=self.outf)
            if "info" in devdict:
                i = 0
                for info_key in devdict["info"]:
                    if not i:
                        print(
                            f"{'info':20} {info_key:40} {devdict['info'][info_key]}",
                            file=self.outf,
                        )
                    else:
                        print(
                            f"{' ':20} {info_key:40} {devdict['info'][info_key]}",
                            file=self.outf,
                        )
                    i += 1
            print_txt("attributes")
            print_txt("commands")
            print_txt("properties")
            print(file=self.outf)

    def print_txt_quick(self) -> None:
        """Print text in short form."""

        def print_attributes() -> None:
            """Print attribute in short form."""
            print(f"{'attributes':20}", end="", file=self.outf)
            i = 0
            for attrib in devdict["attributes"]:
                if not i:
                    print(f" {attrib:40}", end="", file=self.outf)
                else:
                    print(f"{' ':20} {attrib:40}", end="", file=self.outf)
                i += 1
                try:
                    print(f"{devdict['attributes'][attrib]['data']['value']}", file=self.outf)
                except KeyError:
                    print("N/A", file=self.outf)

        def print_commands() -> None:
            """Print commands with values."""
            self.logger.info("Print commands : %s", devdict["commands"])
            print(f"{'commands':20}", end="", file=self.outf)
            i = 0
            for cmd in devdict["commands"]:
                if "value" in devdict["commands"][cmd]:
                    if not i:
                        print(f" {cmd:40}", end="", file=self.outf)
                    else:
                        print(f"{' ':20} {cmd:40}", end="", file=self.outf)
                    i += 1
                    print(f"{devdict['commands'][cmd]['value']}", file=self.outf)

        for device in self.devices_dict:
            devdict = self.devices_dict[device]
            print(f"{'name':20} {devdict['name']}", file=self.outf)
            print(f"{'version':20} {devdict['version']}", file=self.outf)
            print(f"{'versioninfo':20} {devdict['versioninfo'][0]}", file=self.outf)
            # print(f"{'adminMode':20} {devdict['adminMode']}", file=self.outf)
            print_attributes()
            print_commands()
            print(file=self.outf)
