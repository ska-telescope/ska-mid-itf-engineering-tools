"""
Read information from Tango database.
"""
import json
import logging
import os
import socket
import time
from typing import Any, Tuple

import tango
from ska_control_model import AdminMode

from ska_mid_itf_engineering_tools.ska_jargon.ska_jargon import find_jargon  # type: ignore


def check_tango(tango_fqdn: str, tango_port: int = 10000) -> int:
    """
    Check Tango host address.

    :param tango_fqdn: fully qualified domain name
    :param tango_port: port number
    :return: error condition
    """
    try:
        tango_addr = socket.gethostbyname_ex(tango_fqdn)
        tango_ip = tango_addr[2][0]
    except socket.gaierror as e:
        print("Could not read address %s : %s" % (tango_fqdn, e))
        return 1
    print(f"TANGO_HOST={tango_fqdn}:{tango_port}")
    print(f"TANGO_HOST={tango_ip}:{tango_port}")
    return 0


def check_device(dev: tango.DeviceProxy) -> bool:
    try:
        dev.ping()
        return True
    except Exception:
        return False


class TangoDeviceInfo:
    """
    Read and display information about Tango device.
    """

    def __init__(
        self,
        logger: logging.Logger,
        cfg_data: Any,
        device_name: str,
        disp_action: int,
        evrythng: bool,
    ):
        """
        Display Tango device in mark-down format

        :param logger: logging handle
        :param cfg_data: configuration
        :param device_name: device name
        :param disp_action: flag for output format
        :param evrythng: do not filter devices by name
        """
        # Connect to device proxy
        self.logger = logger
        self.dev: tango.DeviceProxy = tango.DeviceProxy(device_name)
        # Read state
        try:
            self.dev_state = self.dev.State()
            self.dev_str = f"{repr(self.dev_state).split('.')[3]}"
        except Exception:
            self.dev_state = None
            self.dev_str = "None"
        try:
            self.dev_name = self.dev.name()
            self.online = True
        except Exception:
            self.dev_name = device_name
            self.online = False
        self.disp_action = disp_action
        self.evrythng = evrythng
        self.on_dev_count = 0
        self.ignore = cfg_data["ignore_device"]
        self.run_commands = cfg_data["run_commands"]
        self.run_commands_name = cfg_data["run_commands_name"]
        try:
            self.adminMode = self.dev.adminMode
        except AttributeError:
            self.adminMode = None

    def check_device(self) -> bool:
        try:
            self.dev.ping()
            return True
        except Exception:
            return False

    def device_state(self) -> None:
        """
        Display status information for Tango device.

        :param dev: Tango device handle
        :return: None
        """
        print(f"Device {self.dev_name}")
        if not self.online:
            return
        print(f"\tAdmin mode                     : {self.adminMode}")
        print(f"\tDevice status                  : {self.dev.Status()}")
        print(f"\tDevice state                   : {self.dev.State()}")
        try:
            print(f"\tObservation state              : {repr(self.dev.obsState)}")
            show_obs_state(self.dev.obsState)
        except AttributeError:
            self.logger.info("Device %s does not have an observation state", self.dev_name)
        print(f"versionId                        : {self.dev.versionId}")
        print(f"build State                      : {self.dev.buildState}")
        print(f"logging level                    : {self.dev.loggingLevel}")
        print(f"logging Targets                  : {self.dev.loggingTargets}")
        print(f"health State                     : {self.dev.healthState}")
        print(f"control Mode                     : {self.dev.controlMode}")
        print(f"simulation Mode                  : {self.dev.simulationMode}")
        print(f"test Mode                        : {self.dev.testMode}")
        print(f"long Running Commands In Queue   : {self.dev.longRunningCommandsInQueue}")
        print(f"long Running Command IDs InQueue : {self.dev.longRunningCommandIDsInQueue}")
        print(f"long Running Command Status      : {self.dev.longRunningCommandStatus}")
        print(f"long Running Command Progress    : {self.dev.longRunningCommandProgress}")
        print(f"long Running Command Result      : {self.dev.longRunningCommandResult}")

    def get_tango_admin(self) -> bool:
        """
        Read admin mode for Tango device.

        :return: True when device is in admin mode
        """
        csp_admin = self.dev.adminMode
        if csp_admin == AdminMode.ONLINE:
            print("Device admin mode online")
            return False
        if csp_admin == AdminMode.OFFLINE:
            print("Device admin mode offline")
        else:
            print(f"Device admin mode {csp_admin}")
        return True

    def set_tango_admin(self, dev_adm: bool, sleeptime: int = 2) -> bool:
        """
        Write admin mode for a Tango device.

        :param dev_adm: admin mode flag
        :param sleeptime: seconds to sleep
        :return: True when device is in admin mode
        """
        print(f"*** Set Adminmode to {dev_adm} and check state ***")
        if dev_adm:
            self.dev.adminMode = 1
        else:
            self.dev.adminMode = 0
        time.sleep(sleeptime)
        return self.get_tango_admin()

    def run_command(self, cmd: str, args: Any = None) -> None:
        """
        Run command and get output.
        :param cmd: command name
        :param args: arguments for command
        :return: None
        """
        try:
            if args:
                inout = self.dev.command_inout(cmd, args)
            else:
                inout = self.dev.command_inout(cmd)
        except tango.DevFailed as terr:
            print(f"{cmd:17} : <ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m")
            return
        print(f"{cmd:17} : {inout}")

    def show_device_command(self, prefix: str, cmd: Any) -> None:
        lpre = "\n" + f"{' ':67}"
        print(f"{prefix:17}   \033[1m{cmd.cmd_name:30}\033[0m", end="")
        if self.dev.is_command_polled(cmd.cmd_name):
            print(" Polled     ", end="")
        else:
            print(" Not polled ", end="")
        in_type_desc = cmd.in_type_desc
        if in_type_desc != "Uninitialised":
            if "\n" in in_type_desc:
                in_type_desc = in_type_desc[:-1].replace("\n", lpre)
            print(f" IN  {in_type_desc}")
        else:
            in_type_desc = ""
        out_type_desc = cmd.out_type_desc
        if out_type_desc != "Uninitialised":
            if in_type_desc:
                print(f"{' ':63}", end="")
            else:
                print(" ", end="")
            if "\n" in out_type_desc:
                out_type_desc = out_type_desc[:-1].replace("\n", lpre)
            print(f"OUT {out_type_desc}")
        else:
            out_type_desc = ""
        if in_type_desc == "" and out_type_desc == "":
            print()
        # if self.evrythng and in_type_desc == "Uninitialised":
        #     run_cmd = self.dev.command_inout(cmd)

    def show_device_commands(self) -> None:
        """
        Print commands.
        :return: None
        """
        try:
            cmds = self.dev.get_command_config()
        except Exception:
            cmds = []
        if cmds:
            cmd = cmds[0]
            self.show_device_command("Commands", cmd)
            for cmd in cmds[1:]:
                self.show_device_command(" ", cmd)

    def run_device_commands(self, cmds: tuple) -> None:
        """
        Run applicable commands and print result.
        :param cmds:
        :return:
        """
        # print(f"{'Run commands':17} : {len(cmds)}")
        for cmd in cmds:
            if cmd in self.run_commands:
                self.run_command(cmd)
            elif cmd in self.run_commands_name:
                self.run_command(cmd, self.dev_name)
            else:
                pass

    def show_attribute_value_scalar(self, prefix: str, attrib_value: str) -> None:  # noqa: C901
        """
        Print attribute value.
        :param prefix: data prefix string
        :param attrib_value: attribute value
        """
        try:
            attrib_json = json.loads(attrib_value)
        except Exception:
            print(f" '{attrib_value}'")
            return
        print(" <JSON>")
        if type(attrib_json) is dict:
            for value in attrib_json:
                attr_value = attrib_json[value]
                if type(attr_value) is list:
                    for item in attr_value:
                        if type(item) is dict:
                            print(f"{prefix} {value} :")
                            for key in item:
                                print(f"{prefix+'    '} {key} : {item[key]}")
                        else:
                            print(f"{prefix+'    '} {item}")
                elif type(attr_value) is dict:
                    print(f"{prefix} {value}")
                    for key in attr_value:
                        key_value = attr_value[key]
                        if not key_value:
                            print(f"{prefix+'    '} {key} ?")
                        elif type(key_value) is str:
                            if key_value[0] == "{":
                                print(f"{prefix+'    '} {key} : DICT{key_value}")
                            else:
                                print(f"{prefix+'    '} {key} : STR{key_value}")
                        else:
                            print(f"{prefix+'    '} {key} : {key_value}")
                else:
                    print(f"{prefix} {value} : {attr_value}")
        elif type(attrib_json) is list:
            for value in attrib_json:
                print(f"{prefix} {value}")
        else:
            print(f" '{attrib_value}' (type {type(attrib_value)})")

    def show_attribute_value_spectrum(self, prefix: str, attrib_value: str) -> None:
        """
        Print attribute value
        :param prefix: data prefix string
        :param attrib_value: attribute value
        """
        if type(attrib_value) is tuple:
            print()
            for attr in attrib_value:
                print(f"{prefix}   {attr}")
        elif type(attrib_value) is dict:
            int_models = json.loads(attrib_value)
            for key in int_models:
                print(f"{prefix}   {key}")
                int_model_values = int_models[key]
                if type(int_model_values) is dict:
                    for value in int_model_values:
                        print(f"{prefix+'     '} {value} : {int_model_values[value]}")
                else:
                    print(f"{prefix+'     '} {value} : {int_model_values}")
        elif attrib_value is None:
            print(" <None>")
        else:
            print(f" {type(attrib_value)}:{attrib_value}")

    def show_attribute_value(self, attrib: str, prefix: str, dry_run: bool) -> None:  # noqa: C901
        """
        Print attribute value
        :param attrib: attribute name
        :param prefix: data prefix string
        """
        if not dry_run:
            try:
                attrib_value = self.dev.read_attribute(attrib).value
                self.logger.debug("Attribute %s value %s", attrib, attrib_value)
            except tango.DevFailed as terr:
                print(f" <ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m")
                attrib_value = None
            except Exception:
                print(" <could not be read>")
                attrib_value = None
        else:
            print(" <N/A>")
            attrib_value = None
        try:
            attrib_cfg = self.dev.get_attribute_config(attrib)
        except tango.ConnectionFailed:
            print(" <connection failed>")
            return
        data_format = attrib_cfg.data_format
        # print(f" ({data_format})", end="")
        if not dry_run and attrib_value is not None:
            # pylint: disable-next=c-extension-no-member
            if data_format == tango._tango.AttrDataFormat.SCALAR:
                self.show_attribute_value_scalar(prefix, attrib_value)
            # pylint: disable-next=c-extension-no-member
            elif data_format == tango._tango.AttrDataFormat.SPECTRUM:
                self.show_attribute_value_spectrum(prefix, attrib_value)
            else:
                print(f" {attrib_value}")
        # else:
        #     print(" <N/A>")
        if self.dev.is_attribute_polled(attrib):
            print(f"{prefix} Polled")
        else:
            print(f"{prefix} Not polled")
        events = attrib_cfg.events.arch_event.archive_abs_change
        print(f"{prefix} Event change : {events}")
        if not dry_run and attrib_value is not None:
            try:
                print(f"{prefix} Quality : {self.dev.read_attribute(attrib).quality}")
            except tango.ConnectionFailed:
                print(f"{prefix} Quality : <connection failed>")
        else:
            print(f"{prefix} Quality : <N/A>")

    def show_device_attributes(self, dry_run: bool) -> None:
        """
        Print attributes
        :return: None
        """
        try:
            attribs = sorted(self.dev.get_attribute_list())
        except Exception:
            attribs = []
        if attribs:
            attrib = attribs[0]
            print(f"{'Attributes':17} : \033[1m{attrib:30}\033[0m", end="")
            self.show_attribute_value(attrib, " " * 50, dry_run)
            for attrib in attribs[1:]:
                print(f"{' ':17}   \033[1m{attrib:30}\033[0m", end="")
                self.show_attribute_value(attrib, " " * 50, dry_run)

    def show_device_properties(self, dry_run: bool) -> None:  # noqa: C901
        """
        Print attributes
        :return: None
        """
        try:
            props = sorted(self.dev.get_property_list("*"))
        except Exception as terr:
            self.logger.info(f"{terr}")
            props = []
        if len(props) == 1:
            prop = props[0]
            prop_values = self.dev.get_property(prop)
            prop_list = prop_values[prop]
            print(f"{'Properties':17} : \033[1m{prop:30}\033[0m {prop_list[0]}")
        if props:
            prop = props[0]
            prop_values = self.dev.get_property(prop)
            prop_list = prop_values[prop]
            if len(prop_list) == 1:
                print(f"{'Properties':17} : \033[1m{prop:30}\033[0m {prop_list[0]}")
            elif len(prop_list[0]) > 30 and len(prop_list[1]) > 30:
                print(f"{'Properties':17} : \033[1m{prop:30}\033[0m {prop_list[0]}")
                for prop_val in prop_list[1:]:
                    print(f"{' ':17}   {' ':30} {prop_val}")
            else:
                print(
                    f"{'Properties':17} : \033[1m{prop:30}\033[0m {prop_list[0]} "
                    f" {prop_list[1]}"
                )
                n = 2
                while n < len(prop_list):
                    print(f"{' ':17}   {' ':30} {prop_list[n]}  {prop_list[n+1]}")
                    n += 2
            for prop in props[1:]:
                prop_values = self.dev.get_property(prop)
                prop_list = prop_values[prop]
                if len(prop_list) == 1:
                    print(f"{' ':17}   \033[1m{prop:30}\033[0m {prop_list[0]}")
                elif len(prop_list[0]) > 30 and len(prop_list[1]) > 30:
                    print(f"{' ':17}   \033[1m{prop:30}\033[0m {prop_list[0]}")
                    for prop_val in prop_list[1:]:
                        print(f"{' ':17}   {' ':30} {prop_val}")
                else:
                    print(f"{' ':17}   \033[1m{prop:30}\033[0m {prop_list[0]}  {prop_list[1]}")
                    n = 2
                    while n < len(prop_list):
                        print(f"{' ':17}   {' ':30} {prop_list[n]}  {prop_list[n+1]}")
                        n += 2
        else:
            print(f"{'Properties':17} : <NONE>")

    def show_device_query(self) -> int:  # noqa: C901
        """
        Display Tango device in text format

        :return: one if device is on, otherwise zero
        """
        rv = 1
        # pylint: disable-next=c-extension-no-member
        print(f"{'Device':17} : {self.dev_name}", end="")
        if not self.online:
            print(" <error>")
            return 0
        # pylint: disable-next=c-extension-no-member
        # if self.dev_state != tango._tango.DevState.ON:
        #     if not self.evrythng:
        #         print(f"\n{'State':17} : OFF\n")
        #         return 0
        #     rv = 0
        try:
            cmds = self.dev.get_command_list()
        except Exception:
            cmds = []
        print(f" {len(cmds)} \033[3mcommands\033[0m,", end="")
        try:
            attribs = sorted(self.dev.get_attribute_list())
        except Exception:
            attribs = []
        print(f" {len(attribs)} \033[1mattributes\033[0m")
        if self.adminMode is not None:
            print(f"{'Admin mode':17} : {self.adminMode}")
        dev_info = self.dev.info()
        if "State" in cmds:
            print(f"{'State':17} : {self.dev.State()}")
        if "Status" in cmds:
            dev_status = self.dev.Status().replace("\n", f"\n{' ':20}")
            print(f"{'Status':17} : {dev_status}")
        print(f"{'Description':17} : {self.dev.description()}")
        jargon = find_jargon(self.dev_name)
        if jargon:
            print(f"{'Acronyms':17} : {jargon}")
        print(f"{'Device class':17} : {dev_info.dev_class}")
        print(f"{'Server host':17} : {dev_info.server_host}")
        print(f"{'Server ID':17} : {dev_info.server_id}")
        if "DevLockStatus" in cmds:
            print(f"{'Lock status':17} : {self.dev.DevLockStatus(self.dev_name)}")
        if "DevPollStatus" in cmds:
            print(f"{'Poll status':17} : {self.dev.DevPollStatus(self.dev_name)}")
        # Get Logging Target
        if "GetLoggingTarget" in cmds:
            qdevs = self.dev.GetLoggingTarget(self.dev_name)
            if qdevs:
                qdev = qdevs[0]
                print(f"{'Logging target':17} : {qdev}")
                for qdev in qdevs[1:]:
                    print(f"{' ':17} : {qdev}")
            else:
                print(f"{'Logging target':17} : none specified")
        else:
            print(f"{'Logging target':17} : <N/A>")
        # Print query classes
        if "QueryClass" in cmds:
            qdevs = self.dev.QueryClass()
            if qdevs:
                qdev = qdevs[0]
                print(f"{'Query class':17} : {qdev}")
                for qdev in qdevs[1:]:
                    print(f"{' ':17} : {qdev}")
            else:
                print(f"{'Query class':17} : none specified")
        # else:
        #     print(f"{'Query class':17} : <N/A>")
        # Print query devices
        if "QueryDevice" in cmds:
            qdevs = self.dev.QueryDevice()
            if qdevs:
                qdev = qdevs[0]
                print(f"{'Query devices':17} : {qdev}")
                for qdev in qdevs[1:]:
                    print(f"{' ':17} : {qdev}")
            else:
                print(f"{'Query devices':17} : none specified")
        # else:
        #     print(f"{'Query devices':17} : <N/A>")
        # Print query sub-devices
        if "QuerySubDevice" in cmds:
            qdevs = self.dev.QuerySubDevice()
            if qdevs:
                qdev = qdevs[0]
                print(f"{'Query sub-devices':17} : {qdev}")
                for qdev in qdevs[1:]:
                    print(f"{' ':17} : {qdev}")
            else:
                print(f"{'Query sub-devices':17} : none specified")
        else:
            print(f"{'Query sub-devices':17} : <N/A>")
        print("")
        return rv

    def show_device_list(self) -> int:  # noqa: C901
        """
        Display Tango device in text format
        :return: one if device is on, otherwise zero
        """
        # pylint: disable-next=c-extension-no-member
        if not self.evrythng:
            dev1 = self.dev_name.split("/")[0]
            if dev1 in self.ignore:
                return 0
        if not self.online:
            print(f"{self.dev_name:40} <offline>")
            return 0
        print(f"{self.dev_name:40}", end="")
        rv = 1
        cmds: tuple = ()
        try:
            cmds = self.dev.get_command_list()
        except Exception:
            cmds = ()
        # try:
        #     attribs = sorted(self.dev.get_attribute_list())
        # except Exception:
        #     attribs = []
        # dev_info = self.dev.info()
        if "State" in cmds:
            try:
                print(f" {self.dev.State()}", end="")
            except tango.ConnectionFailed:
                print(f"{'State':17} : <connection failed>\n")
                return 0
        else:
            print("N/A", end="")
        if self.adminMode is not None:
            print(f" (admin {self.adminMode})")
        else:
            print()
        return rv

    def show_device_short(self) -> int:  # noqa: C901
        """
        Display Tango device in text format
        :return: one if device is on, otherwise zero
        """
        # pylint: disable-next=c-extension-no-member
        if not self.evrythng:
            dev1 = self.dev_name.split("/")[0]
            if dev1 in self.ignore:
                # print(f"{'Device':17} :  skip {dev1}\n")
                return 0
        if not self.online:
            print(f"{'Device':17} : {self.dev_name} <offline>\n")
            return 0
        print(f"{'Device':17} : {self.dev_name}")
        if self.adminMode is not None:
            print(f"{'Admin mode':17} : {self.adminMode}")
        rv = 1
        # pylint: disable-next=c-extension-no-member
        # if self.dev_state != tango._tango.DevState.ON:
        #     if not self.evrythng:
        #         print(f"{'State':17} : OFF\n")
        #         return 0
        #     rv = 0
        # else:
        #     print(f" <ON>", end="")
        cmds: tuple = ()
        try:
            cmds = self.dev.get_command_list()
        except Exception:
            cmds = ()
        # print(f" {len(cmds)} \033[3mcommands\033[0m,", end="")
        try:
            attribs = sorted(self.dev.get_attribute_list())
        except Exception:
            attribs = []
        # dev_info = self.dev.info()
        if "State" in cmds:
            try:
                print(f"{'State':17} : {self.dev.State()}")
            except tango.ConnectionFailed:
                print(f"{'State':17} : <connection failed>\n")
                return 0
        if "Status" in cmds:
            try:
                dev_status = self.dev.Status().replace("\n", f"\n{' ':20}")
                print(f"{'Status':17} : {dev_status}")
            except tango.ConnectionFailed:
                print(f"{'Status':17} : <connection failed>\n")
                return 0
        if cmds:
            print(f"{'Commands':17} : {cmds[0]}")
            for cmd in cmds[1:]:
                print(f"{' ':17} : {cmd}")
        # Print attributes in bold
        if attribs:
            print(f"{'Attributes':17} : {attribs[0]}")
            for attrib in attribs[1:]:
                print(f"{' ':17} : {attrib}")
        try:
            props = self.dev.get_property_list("*")
        except Exception:
            cmds = ()
        if props:
            print(f"{'Properties':17} : {props[0]}")
            for prop in props[1:]:
                print(f"{' ':17} : {prop}")
        print()
        return rv

    def show_device_all(self, dry_run: bool) -> int:  # noqa: C901
        """
        Display Tango device in text format
        :return: one if device is on, otherwise zero
        """
        # pylint: disable-next=c-extension-no-member
        print(f"{'Device':17} : {self.dev_name}", end="")
        if not self.evrythng:
            dev1 = self.dev_name.split("/")[0]
            if dev1 in self.ignore:
                print(f" skip {dev1}\n")
                return 0
        if not self.online:
            print(" <offline>\n")
            return 0
        print()
        rv = 1
        if self.adminMode is not None:
            print(f"{'Admin mode':17} : {self.adminMode}")
        cmds: tuple = ()
        try:
            cmds = self.dev.get_command_list()
        except Exception:
            cmds = ()
        dev_info = self.dev.info()
        if "State" in cmds:
            try:
                print(f"{'State':17} : {self.dev.State()}")
            except tango.ConnectionFailed:
                print(f"{'State':17} : <connection failed>")
                return 0
        if "Status" in cmds:
            try:
                dev_status = self.dev.Status().replace("\n", f"\n{' ':20}")
                print(f"{'Status':17} : {dev_status}")
            except tango.ConnectionFailed:
                print(f"{'Status':17} : <connection failed>")
                return 0
        print(f"{'Description':17} : {self.dev.description()}")
        jargon = find_jargon(self.dev_name)
        if jargon:
            print(f"{'Acronyms':17} : {jargon}")
        print(f"{'Database used':17} : {self.dev.is_dbase_used()}")
        print(f"{'Device class':17} : {dev_info.dev_class}")
        print(f"{'Server host':17} : {dev_info.server_host}")
        print(f"{'Server ID':17} : {dev_info.server_id}")
        try:
            print(f"{'Resources'} : {self.dev.assignedresources}")
        except tango.DevFailed as terr:
            print(f"{'Resources':17} :")
            print(f" <ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m")
        except AttributeError:
            pass
        try:
            print(f"{'VCC state':17} : {self.dev.assignedVccState}")
        except AttributeError:
            pass
        try:
            dev_obs = self.dev.obsState
            print(f"{'Observation':17} : {get_obs_state(dev_obs)}")
        except Exception:
            pass
        # Print commands in italic
        self.show_device_commands()
        # Run commands deemed to be safe
        self.run_device_commands(cmds)
        # Print attributes in bold
        self.show_device_attributes(dry_run)
        # Print properties in bold
        self.show_device_properties(dry_run)
        return rv

    def show_device_markdown(self) -> int:  # noqa: C901
        """
        Display Tango device in mark-down format.
        """
        rval = 0
        print(f"## Device *{self.dev_name}*")
        if not self.online:
            print("Error")
            return rval
        # Read database host
        print(f"### Database host\n{self.dev.get_db_host()}")
        if self.dev_state is not None:
            print(f"### State\n{self.dev_state}")
        else:
            print("### State\nNONE")
        # Read information
        try:
            print(f"### Information\n```\n{self.dev.info()}\n```")
        except Exception:
            print("### Information\n```\nNONE\n```")
        # Read commands
        try:
            cmds = sorted(self.dev.get_command_list())
            # Display version information
            if "GetVersionInfo" in cmds:
                verinfo = self.dev.GetVersionInfo()
                print(f"### Version\n```\n{verinfo[0]}\n```")
            # Display commands
            print("### Commands")
            print("```\n%s\n```" % "\n".join(cmds))
            # Read command configuration
            cmd_cfgs = self.dev.get_command_config()
            for cmd_cfg in cmd_cfgs:
                print(f"#### Command *{cmd_cfg.cmd_name}*")
                # print(f"```\n{cmd_cfg}\n```")
                print("|Name |Value |")
                print("|:----|:-----|")
                if cmd_cfg.cmd_tag != 0:
                    print(f"|cmd_tag|{cmd_cfg.cmd_tag}|")
                print(f"|disp_level|{cmd_cfg.disp_level}|")
                print(f"|in_type|{cmd_cfg.in_type}|")
                if cmd_cfg.in_type_desc != "Uninitialised":
                    print(f"|in_type|{cmd_cfg.in_type_desc}")
                print(f"|out_type|{cmd_cfg.out_type}|")
                if cmd_cfg.out_type_desc != "Uninitialised":
                    print(f"|in_type|{cmd_cfg.out_type_desc}")
        except Exception:
            cmds = []
            print("### Commands\n```\nNONE\n```")
        # Read status
        if "Status" in cmds:
            print(f"#### Status\n{self.dev.Status()}")
        else:
            print("#### Status\nNo Status command")
        # Read attributes
        print("### Attributes")
        # pylint: disable-next=c-extension-no-member
        if self.dev_state == tango._tango.DevState.ON:
            rval = 1
            attribs = sorted(self.dev.get_attribute_list())
            print("```\n%s\n```" % "\n".join(attribs))
            for attrib in attribs:
                print(f"#### Attribute *{attrib}*")
                try:
                    print("##### Value\n```\n{self.dev.read_attribute(attrib).value}\n```")
                except Exception:
                    print(f"```\n{attrib} could not be read\n```")
                try:
                    attrib_cfg = self.dev.get_attribute_config(attrib)
                    print(f"##### Description\n```\n{attrib_cfg.description}\n```")
                    # print(f"##### Configuration\n```\n{attrib_cfg}\n```")
                except Exception:
                    print(f"```\n{attrib} configuration could not be read\n```")
        else:
            print("```\nNot reading attributes in offline state\n```")
        print("")
        return rval

    def show_device_state(self) -> int:
        """
        Display Tango device name only.
        """
        # pylint: disable-next=c-extension-no-member
        # if self.dev_state != tango._tango.DevState.ON:
        #     print(f"     {self.dev_name} ({self.adminMode})")
        #     return 0
        # print(f"[ON] {self.dev_name} ({self.adminMode})")
        print(f"{self.dev_str:10} {self.dev_name:40} {self.adminMode}")
        return 1

    def show_device(self, dry_run: bool) -> None:
        """Print device information."""
        if self.disp_action == 6:
            self.on_dev_count += self.show_device_list()
        elif self.disp_action == 5:
            self.on_dev_count += self.show_device_short()
        elif self.disp_action == 4:
            self.on_dev_count += self.show_device_state()
        elif self.disp_action == 3:
            self.on_dev_count += self.show_device_query()
        elif self.disp_action == 2:
            self.on_dev_count += self.show_device_markdown()
        elif self.disp_action == 1:
            self.on_dev_count += self.show_device_all(dry_run)
        else:
            print("Nothing to do!")


def setup_device(logger: logging.Logger, dev_name: str) -> Tuple[int, tango.DeviceProxy]:
    """
    Set up device connection and timeouts.

    :param logger: logging handle
    :param dev_name: Tango device name
    :return: error condition and Tango device handle
    """
    print("*** Setup Device connection and Timeouts ***")
    print(f"Tango device : {dev_name}")
    dev = tango.DeviceProxy(dev_name)
    # check AdminMode
    csp_admin = dev.adminMode
    if csp_admin:
        # Set Adminmode to OFFLINE and check state
        dev.adminMode = 0
        csp_admin = dev.adminMode
        if csp_admin:
            logger.error("Could not turn off admin mode")
            return 1, None
    return 0, dev


SAFE_COMMANDS = ["DevLockStatus"]


def list_devices(
    logger: logging.Logger,
    cfg_data: Any,
    evrythng: bool,
    itype: str | None,
) -> list:
    """
    Get a list of devices
    :param logger: logging handle
    :param cfg_data: configuration data in JSON format
    :param evrythng: get commands and attributes regadrless of state
    :param itype: filter device name
    :return:
    """
    devices: list = []

    # Get Tango database host
    tango_host = os.getenv("TANGO_HOST")
    print(f"{'Tango host':17} : {tango_host}\n")

    # Connect to database
    try:
        database = tango.Database()
    except Exception:
        logger.error("Could not connect to Tango database %s", tango_host)
        return devices
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
                logger.debug("'%s' matches '%s'", device, cfg_data["ignore_device"])
                continue
        if itype:
            iupp = device.upper()
            if itype not in iupp:
                logger.info(f"Ignore {device}")
                continue
        logger.info("Add device %s", device)
        devices.append(device)
    return devices


def show_devices(
    logger: logging.Logger,
    cfg_data: Any,
    disp_action: int,
    evrythng: bool,
    itype: str | None,
    dry_run: bool,
) -> None:  # noqa: C901
    """
    Display information about Tango devices

    :param logger: logging handle
    :param cfg_data: configuration data in JSON format
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param itype: filter device name
    :param dry_run: do not read attributes
    """
    # Get Tango database host
    tango_host = os.getenv("TANGO_HOST")
    # print("Tango host %s" % tango_host)

    devices = list_devices(logger, cfg_data, evrythng, itype)
    logger.info("Read %d devices" % (len(devices)))

    # Mark-down foreword
    if disp_action == 2:
        print("# Tango devices")
        print("## Tango host\n```\n%s\n```" % tango_host)
        print(f"## Number of devices\n{len(devices)}")
    elif disp_action == 4:
        print(f"{'STATE':10} {'DEVICE NAME':40} ADMIN MODE")

    dev_count = 0
    on_dev_count = 0
    for device in devices:
        dev_count += 1
        try:
            tgo_info = TangoDeviceInfo(logger, cfg_data, device, disp_action, evrythng)
        except tango.DevFailed as terr:
            print(f"{device} : <ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m")
            continue
        tgo_info.show_device(dry_run)

    # Mark-down summary
    if disp_action == 2:
        if itype:
            print("## Summary")
            print(f"Found {dev_count} devices matching {itype}")
        else:
            print("## Summary")
            print(f"Found {dev_count} devices")
        print(f"There are {on_dev_count} active devices")
        print("# Kubernetes pod\n>", end="")


def check_command(logger: logging.Logger, dev: Any, c_name: str | None) -> list:
    """
    Read commands from database.
    :param logger: logging handle
    :param dev: device handle
    :param c_name: command name
    :return: list of commands
    """
    cmds_found: list = []
    if c_name is None:
        return cmds_found
    try:
        cmds = sorted(dev.get_command_list())
    except Exception:
        cmds = []
    logger.info("Check commands %s", cmds)
    c_name = c_name.lower()
    for cmd in sorted(cmds):
        if c_name in cmd.lower():
            cmds_found.append(cmd)
    return cmds_found


def show_attributes(  # noqa: C901
    logger: logging.Logger, disp_action: int, evrythng: bool, a_name: str | None
) -> None:
    """
    Display information about Tango devices

    :param logger: logging handle
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param a_name: filter attribute name
    """
    if a_name is None:
        return

    # Get Tango database hist
    tango_host = os.getenv("TANGO_HOST")
    logger.info("Tango host %s" % tango_host)

    # Connect to database
    try:
        database = tango.Database()
    except Exception:
        logger.error("Could not connect to Tango database %s", tango_host)
        return
    # Read devices
    device_list = database.get_device_exported("*")
    logger.info(f"{len(device_list)} devices available")

    logger.info("Read %d devices" % (len(device_list)))
    if disp_action == 2:
        print("# Tango devices")
        print("## Tango host\n```\n%s\n```" % tango_host)
        print(f"## Number of devices\n{len(device_list)}")

    for device in sorted(device_list.value_string):
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        try:
            attribs = sorted(dev.get_attribute_list())
        except Exception:
            attribs = []
        # Check attribute names
        a_name = a_name.lower()
        attribs_found = []
        for attrib in sorted(attribs):
            if a_name in attrib.lower():
                attribs_found.append(attrib)
        if attribs_found:
            print(f"{device:48}", end="")
            print(f" \033[1m{attribs_found[0]}\033[0m")
            for attrib in attribs_found[1:]:
                print(f"{' ':48} \033[1m{attrib}\033[0m")


def show_commands(
    logger: logging.Logger, disp_action: int, evrythng: bool, c_name: str | None
) -> None:
    """
    Display information about Tango devices

    :param logger: logging handle
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param c_name: filter command name
    """
    if c_name is None:
        return

    # Get Tango database host
    tango_host = os.getenv("TANGO_HOST")
    logger.info("Tango host %s" % tango_host)

    # Connect to database
    try:
        database = tango.Database()
    except Exception:
        logger.error("Could not connect to Tango database %s", tango_host)
        return
    # Read devices
    device_list = database.get_device_exported("*")
    logger.info(f"{len(device_list)} devices available")

    logger.info("Read %d devices" % (len(device_list)))

    for device in sorted(device_list.value_string):
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        chk_cmds = check_command(logger, dev, c_name)
        if chk_cmds:
            print(f"{dev.name():48}", end="")
            print(f" \033[1m{chk_cmds[0]}\033[0m")
            for chk_cmd in chk_cmds[1:]:
                print(f"{' ':48} \033[1m{chk_cmd}\033[0m")


def show_properties(
    logger: logging.Logger, disp_action: int, evrythng: bool, p_name: str | None
) -> None:
    """
    Display information about Tango devices

    :param logger: logging handle
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param p_name: filter command name
    """
    if p_name is None:
        return

    # Get Tango database host
    tango_host = os.getenv("TANGO_HOST")
    logger.info("Tango host %s" % tango_host)

    # Connect to database
    try:
        database = tango.Database()
    except Exception:
        logger.error("Could not connect to Tango database %s", tango_host)
        return
    # Read devices
    device_list = database.get_device_exported("*")
    logger.info(f"{len(device_list)} devices available")

    logger.info("Read %d devices" % (len(device_list)))

    p_name = p_name.lower()
    for device in sorted(device_list.value_string):
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        prop_list = dev.get_property_list("*")
        props_found = []
        for prop in prop_list:
            if p_name in prop.lower():
                props_found.append(prop)
        if props_found:
            print(f"{dev.name():48}", end="")
            print(f" \033[1m{props_found[0]}\033[0m")
            for prop in props_found[1:]:
                print(f"{' ':48} \033[1m{prop}\033[0m")


OBSERVATION_STATES = [
    "EMPTY",
    "RESOURCING",
    "IDLE",
    "CONFIGURING",
    "READY",
    "SCANNING",
    "ABORTING",
    "ABORTED",
    "RESETTING",
    "FAULT",
    "RESTARTING",
]


def get_obs_state(obs_stat: int) -> str:
    """
    Display Python enumerated type for observing state.

    :param obs_stat: observing state numeric value
    :return: state description
    """
    return OBSERVATION_STATES[obs_stat]


def show_obs_state(obs_stat: int) -> None:  # noqa: C901
    """
    Display Python enumerated type for observing state.

    :param obs_stat: observing state numeric value
    """

    if obs_stat == 0:
        # EMPTY = 0
        print(
            """EMPTY:
        The sub-array has no resources allocated and is unconfigured.
        """
        )
    elif obs_stat == 1:
        # RESOURCING = 1
        # In normal science operations these will be the resources required
        # for the upcoming SBI execution.
        #
        # This may be a complete de/allocation, or it may be incremental. In
        # both cases it is a transient state; when the resourcing operation
        # completes, the subarray will automatically transition to EMPTY or
        # IDLE, according to whether the subarray ended up having resources or
        # not.
        #
        # For some subsystems this may be a very brief state if resourcing is
        # a quick activity.
        print(
            """RESOURCING:
        Resources are being allocated to, or deallocated from, the subarray.
        """
        )
    elif obs_stat == 2:
        # IDLE = 2
        print(
            """IDLE:
        The subarray has resources allocated but is unconfigured.
        """
        )
    elif obs_stat == 3:
        # CONFIGURING = 3
        print(
            """CONFIGURING:
        The subarray is being configured for an observation.
        This is a transient state; the subarray will automatically
        transition to READY when configuring completes normally.
        """
        )
    elif obs_stat == 4:
        # READY = 4
        print(
            """READY:
        The subarray is fully prepared to scan, but is not scanning.
        It may be tracked, but it is not moving in the observed coordinate
        system, nor is it taking data.
        """
        )
    elif obs_stat == 5:
        # SCANNING = 5
        print(
            """SCANNING:
        The subarray is scanning.
        It is taking data and, if needed, all components are synchronously
        moving in the observed coordinate system.
        Any changes to the sub-systems are happening automatically (this
        allows for a scan to cover the case where the phase centre is moved
        in a pre-defined pattern).
        """
        )
    elif obs_stat == 6:
        # ABORTING = 6
        print(
            """ABORTING:
         The subarray has been interrupted and is aborting what it was doing.
        """
        )
    elif obs_stat == 7:
        # ABORTED = 7
        print("""ABORTED: The subarray is in an aborted state.""")
    elif obs_stat == 8:
        # RESETTING = 8
        print(
            """RESETTING:
        The subarray device is resetting to a base (EMPTY or IDLE) state.
        """
        )
    elif obs_stat == 9:
        # FAULT = 9
        print(
            """FAULT:
        The subarray has detected an error in its observing state.
        """
        )
    elif obs_stat == 10:
        # RESTARTING = 10
        print(
            """RESTARTING:
        The subarray device is restarting.
        After restarting, the subarray will return to EMPTY state, with no
        allocated resources and no configuration defined.
        """
        )
    else:
        print(f"Unknown state {obs_stat}")


def show_long_running_command(dev: Any) -> int:
    """
    Display long-running command.

    :param dev: Tango device handle
    :return: error condition
    """
    rc = len(dev.longRunningCommandsInQueue)
    print(f"Long running commands on device {dev.name()} : {rc} items")
    print("\tCommand IDs In Queue :")
    for qcmd in dev.longRunningCommandIDsInQueue:
        print(f"\t\t{qcmd}")
    print("\tCommand Progress :")
    for qcmd in dev.longRunningCommandProgress:
        print(f"\t\t{qcmd}")
    print("\tCommand Result :")
    n = 0
    lstat = len(dev.longRunningCommandResult)
    while n < lstat:
        print(f"\t\t{dev.longRunningCommandResult[n]}", end="")
        print(f"\t{dev.longRunningCommandResult[n+1]}", end="")
        print()
        n += 2
    print("\tCommand Status :")
    n = 0
    lstat = len(dev.longRunningCommandStatus)
    while n < lstat:
        print(f"\t\t{dev.longRunningCommandStatus[n+1]:12}", end="")
        print(f"\t{dev.longRunningCommandStatus[n]}")
        n += 2
    print("\tCommands In Queue :")
    for qcmd in dev.longRunningCommandsInQueue:
        print(f"\t\t{qcmd}")
    return rc


def show_long_running_commands(dev_name: str) -> int:
    """
    Display long-running commands.

    :param dev_name: Tango device name
    :return: None
    """
    dev = tango.DeviceProxy(dev_name)
    show_long_running_command(dev)
    return 0


def show_command_inputs(logger: logging.Logger, tango_host: str, tgo_in_type: str) -> None:
    """
    Display commands with given input type.
    :param logger: logging handle
    :param tango_host: Tango database host address and port
    :param tgo_in_type: input type, e.g. Uninitialised
    :return:
    """

    # Connect to database
    try:
        database = tango.Database()
    except Exception:
        logger.error("Could not connect to Tango database %s", tango_host)
        return
    # Read devices
    device_list = database.get_device_exported("*")
    logger.info(f"{len(device_list)} devices available")

    logger.info("Read %d devices" % (len(device_list)))

    for device in sorted(device_list.value_string):
        dev, _dev_state = tango.DeviceProxy(device)
        try:
            cmds = dev.get_command_config()
        except Exception:
            cmds = []
        if cmds:
            for cmd in cmds:
                in_type_desc = cmd.in_type_desc.lower()
                logger.info("Command %s type %s", cmd, in_type_desc)
                if in_type_desc == tgo_in_type:
                    print(f"{'Commands':17} : \033[3m{cmd.cmd_name}\033[0m ({in_type_desc})")
                else:
                    print(f"{'Commands':17} : {cmd.cmd_name} ({in_type_desc})")
    return
