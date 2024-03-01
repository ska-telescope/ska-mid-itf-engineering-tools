"""Read and display Tango stuff."""
import ast
import json
import logging
import re


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


def md_print(inp: str, end: str = "\n") -> None:
    """
    Print markdown string.

    :param inp: input
    """
    # print(inp.replace("/", "\\/").replace("_", "\\_").replace("-", "\\-"), end=end)
    print(inp.replace("_", "\\_").replace("-", "\\-"), end=end)


class TangoJsonReader:

    def __init__(self, logger: logging.Logger, devsdict: dict):
        self.logger = logger
        self.devices_dict = devsdict

    def print_markdown_all(self):
        """Print the whole thing."""

        def print_attribute_data(item: str, dstr: str, dc1, dc2, dc3):
            dc2a = (dc2 / 2) - 3
            dc2b = (dc2 / 2)
            dc3a = (dc3 / 2) - 3
            dc3b = (dc3 / 2)
            # fill = " "
            dstr = re.sub(' +', ' ', dstr)
            md_print(f"| {item:{dc1}} ", end="")
            if dstr[0] == "{" and dstr[-1] == "}":
                ddict = json.loads(dstr)
                self.logger.debug("Print JSON :\n%s", json.dumps(ddict, indent=4))
                n = 0
                for ditem in ddict:
                    if n:
                        print(f"| {' ':{dc1}} ", end="")
                    if type(ddict[ditem]) is dict:
                        m = 0
                        for ditem2 in ddict[ditem]:
                            # if m:
                            #     print(f"| {' ':{dc1}}-| {' ':{dc2}}-", end="")
                            md_print(
                                f"| {ditem:{dc2}} | {ditem2:{dc3a}} "
                                f"| {ddict[ditem][ditem2]:{dc3b}} |"
                            )
                            m += 1
                    elif type(ddict[ditem]) is list:
                        m = 0
                        for ditem2 in ddict[ditem]:
                            self.logger.debug(
                                "Print attribute value list item %s (%s)", ditem2, type(ditem2)
                            )
                            dname = f"{ditem} {m}"
                            if not m:
                                md_print(f"| {dname} ", end="")
                            else:
                                md_print(f"| {' ':{dc1}} | {' ':{dc2}},| {dname} ", end="")
                            md_print(f"| {dname:{dc2}} ", end="")
                            if type(ditem2) is dict:
                                p = 0
                                for ditem3 in ditem2:
                                    # if p:
                                    #     print(f"| {' ':{dc1}},| {' ':{dc2}},| ,", end="")
                                    md_print(f"| {ditem3:{dc2a}} | {ditem2[ditem3]:{dc2b}} |")
                                    p += 1
                            else:
                                md_print(f"| {ditem2:{dc2}}  ||")
                            m += 1
                    else:
                        md_print(f"| {ditem:{dc2}} | {ddict[ditem]:{dc3}} ||")
                    n += 1
            elif dstr[0] == "[" and dstr[-1] == "]":
                dlist = ast.literal_eval(dstr)
                self.logger.debug("Print attribute value list %s (%s)", dlist, type(dlist))
                n = 0
                for ditem in dlist:
                    if n:
                        print(f"| {' ':{dc1}} ", end="")
                    if type(ditem) is dict:
                        m = 0
                        for ditem2 in ditem:
                            if m:
                                print(f"| {' ':{dc1}} ", end="")
                            md_print(f"| {ditem2} | {ditem[ditem2]} |")
                            m += 1
                    else:
                        md_print(f"| {str(ditem):{dc2}} ||")
                    n += 1
            elif "\n" in dstr:
                self.logger.debug("Print attribute value str %s (%s)", dstr, type(dstr))
                n = 0
                for line in dstr.split("\n"):
                    line = line.strip()
                    if line:
                        if n:
                            print(f"| {' ':{dc1}} ", end="")
                        md_print(f"| {line:{dc2}} ||")
                        n += 1
            else:
                md_print(f"| {dstr:{dc2}} ||")
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
                        md_print(f"| {line:{dc3}} |")
                        n += 1
            elif len(dstr) > dc3 and "," in dstr:
                n = 0
                for line in dstr.split(","):
                    if n:
                        if dc2:
                            print(f"| {' ':{dc1}}.| {' ':{dc2}}.", end="")
                        else:
                            print(f"| {' ':{dc1}}.", end="")
                    md_print(f"| {line:{dc3}} |")
                    n += 1
            else:
                md_print(f"| {dstr:{dc3}} |")

        def print_md_attributes():
            ac1 = 30
            ac2 = 50
            ac3 = 90
            print(f"### Attributes\n")
            for attrib in devdict["attributes"]:
                print(f"#### {attrib}\n")
                print("| ITEM | VALUE |       |")
                print("|:-----|:------|:------|")
                attrib_data = devdict["attributes"][attrib]["data"]
                for item in attrib_data:
                    data = attrib_data[item]
                    if type(data) is str:
                        self.logger.debug("Print attribute str %s : %s", item, data)
                        print_attribute_data(item, data, ac1, ac2, ac3)
                    elif type(data) is dict:
                        self.logger.debug("Print attribute dict %s : %s", item, data)
                        n = 0
                        for item2 in data:
                            print_attribute_data(item2, str(data[item2]), ac1, ac2, ac3)
                            n += 1
                    elif type(data) is list:
                        self.logger.debug("Print attribute list %s : %s", item, data)
                        n = 0
                        for item2 in data:
                            if not n:
                                md_print(f"| {item:{ac1}} ", end="")
                            else:
                                print(f"| {' ':{ac1}} ", end="")
                            md_print(f"| {item2:{ac2}} ||")
                            n += 1
                    else:
                        self.logger.warning("Data type for %s (%s) not supported", item, type(data))
                for item in devdict["attributes"][attrib]["config"]:
                    # self.logger.debug("Print config item %s : %s", item, data)
                    config = devdict['attributes'][attrib]['config'][item]
                    print_attribute_data(item, config, ac1, ac2, ac3)
                print()
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
                    md_print(f"| {item:{cc2}} ", end="")
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
                md_print(f"| {prop:{pc1}} ", end="")
                print_data(devdict['properties'][prop]['value'], pc1, 0, pc2)
            print("\n")

        print("# Tango devices in namespace\n")
        for device in self.devices_dict:
            self.logger.info("Print device %s", device)
            devdict = self.devices_dict[device]
            md_print(f"## Device {devdict['name']}\n")
            print("| FIELD | VALUE |")
            print("|:------|:------|")
            print(f"| version | {devdict['version']} |")
            print(f"| Version info | {devdict['versioninfo'][0]} |")
            print(f"| Admin mode | {devdict['adminMode']} |")
            if "info" in devdict:
                print(f"| Device class | {devdict['info']['dev_class']} |")
                print(f"| Server host | {devdict['info']['server_host']} |")
                md_print(f"| Server ID | {devdict['info']['server_id']} |")
            print("\n")
            print_md_attributes()
            print_md_commands()
            print_md_properties()
            print("\n")

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

        for device in self.devices_dict:
            self.logger.info("Print device %s", device)
            devdict = self.devices_dict[device]
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

        for device in self.devices_dict:
            devdict = self.devices_dict[device]
            print(f"{'name':20} {devdict['name']}")
            print(f"{'version':20} {devdict['version']}")
            print(f"{'versioninfo':20} {devdict['versioninfo'][0]}")
            print(f"{'adminMode':20} {devdict['adminMode']}")
            print_attributes()
            print()
