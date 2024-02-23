"""Read and display Tango commands."""
import logging
import os
from typing import Any

import tango

from ska_mid_itf_engineering_tools.tango_info.get_tango_devices import (
    list_devices,
    md_format,
    COLUMN1,
    COLUMN2,
)


class TangoCommandInfo():

    def __init__(self, logger: logging.Logger, dev: Any, cmd: str, args: Any = None):
        """
        Run command and get output.

        :param logger: logging handle
        :param dev: Tango device handle
        :param cmd: command name
        :param args: command arguments
        """
        self.logger = logger
        try:
            if args:
                self.inout = dev.command_inout(cmd, args)
            else:
                self.inout = dev.command_inout(cmd)
        except tango.DevFailed as terr:
            self.inout = f"<ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m"

    def _show_value_txt(self, prefix: str) -> None:
        """
        Print output of command.

        :param prefix: print at front of line
        """
        if type(self.inout) is list:
            if self.inout:
                inout = str(self.inout[0])
            else:
                inout = "[]"
        else:
            inout = str(self.inout)
        if "\n" in inout:
            ios = str(inout).split("\n")
            rval = ios[0]
            for io in ios[1:]:
                rval += f"\n{prefix} {io.strip()}"
        else:
            rval = inout
        print(f" {rval}")

    def _show_value_md(self, prefix: str, suffix: str) -> None:
        """
        Print output of command.

        :param prefix: print at front of line
        """
        if type(self.inout) is list:
            if self.inout:
                inout = str(self.inout[0])
            else:
                inout = "[]"
        else:
            inout = str(self.inout)
        if "\n" in inout:
            ios = str(inout).split("\n")
            rval = ios[0] + suffix
            for io in ios[1:]:
                rval += f"\n{prefix}{io.strip()}{suffix}"
        else:
            rval = f"{prefix}{inout}{suffix}"
        print(f"{rval}")

    def show_value(self, fmt: str, prefix: str, suffix: str):
        if fmt == "md":
            self._show_value_md(prefix, suffix)
        else:
            self._show_value_txt(prefix)


def show_commands(  # noqa: C901
    logger: logging.Logger,
    cfg_data: dict,
    disp_action: int,
    evrythng: bool,
    c_name: str | None,
    dry_run: bool,
    fmt: str,
) -> None:
    """
    Display information about Tango devices.

    :param logger: logging handle
    :param cfg_data: configuration in JSON format
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param c_name: filter command name
    :param dry_run: do not display values
    :param fmt: output format
    """

    # def get_command_inout(prefix: str, idev: Any, cmd: str, args: Any = None) -> Any:
    #     """
    #     Run command and get output.
    #
    #     :param prefix: print at front of line
    #     :param idev: Tango device handle
    #     :param cmd: command name
    #     :param args: arguments for command
    #     """
    #     try:
    #         if args:
    #             inout = idev.command_inout(cmd, args)
    #         else:
    #             inout = idev.command_inout(cmd)
    #     except tango.DevFailed as terr:
    #         return f"<ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m"
    #     if type(inout) is list:
    #         if inout:
    #             inout = str(inout[0])
    #         else:
    #             inout = "[]"
    #     else:
    #         inout = str(inout)
    #     if "\n" in inout:
    #         ios = str(inout).split("\n")
    #         rval = ios[0]
    #         for io in ios[1:]:
    #             rval += f"\n{prefix} {io.strip()}"
    #     else:
    #         rval = inout
    #     return rval

    def filter_command(idev: Any, f_cmd: Any, min_len: int) -> list:
        """
        Print info on device command.

        :param idev: Tango device handle
        :param f_cmd: command name
        :param min_len: minimum string length
        """
        # Read commands
        cmds: tuple = ()
        try:
            cmds = dev.get_command_list()
        except Exception:
            cmds = ()
        logger.debug("Check commands %s", cmds)
        cmds_found = []
        for cmd in cmds:
            if f_cmd in cmd.lower():
                cmds_found.append(cmd)
        logger.info("Found commands %s", cmds_found)
        return cmds_found

    logger.info("Read commans matching %s", c_name)
    if c_name is None:
        return
    c_name = c_name.lower()

    # Get Tango database host
    tango_host = os.getenv("TANGO_HOST")
    logger.info("Tango host %s" % tango_host)

    run_commands = cfg_data["run_commands"]
    logger.info("Run commands %s", run_commands)
    run_commands_name = cfg_data["run_commands_name"]
    logger.info("Run commands with name %s", run_commands_name)
    min_str_len = cfg_data["min_str_len"]

    # Read devices
    device_list = list_devices(logger, cfg_data, evrythng, None)
    logger.info("Read %d devices" % (len(device_list)))

    prefix: str
    suffix: str
    if fmt == "md":
        if not dry_run:
            print("|DEVICE NAME|COMMAND|VALUE|")
            print("|:----------|:------|:----|")
        else:
            print("|DEVICE NAME|COMMAND|")
            print("|:----------|:------|")
        prefix = "|||"
        suffix = "|"
    else:
        if not dry_run:
            print(f"{'DEVICE NAME':{COLUMN1}} {'COMMAND':{COLUMN2}} VALUE")
        else:
            print(f"{'DEVICE NAME':{COLUMN1}} COMMAND")
        prefix = " " * (COLUMN1 + COLUMN2 + 1)
        suffix = ""
    for device in sorted(device_list):
        logger.info("Check device %s", device)
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        chk_cmds = filter_command(dev, c_name, min_str_len)
        if chk_cmds:
            chk_cmd = chk_cmds[0]
            if fmt == "md":
                print(f"|{md_format(device)}|{md_format(chk_cmd)}|", end="")
            else:
                print(f"{device:{COLUMN1}} \033[1m{chk_cmd:{COLUMN2}}\033[0m", end="")
            if not dry_run:
                if chk_cmd in run_commands:
                    tcmd = TangoCommandInfo(logger, dev, chk_cmd)
                    tcmd.show_value(fmt, prefix, suffix)
                elif chk_cmd in run_commands_name:
                    tcmd = TangoCommandInfo(logger, dev, chk_cmd, dev.name())
                    tcmd.show_value(fmt, prefix, suffix)
                else:
                    print(" N/A")
            else:
                print()
            for chk_cmd in chk_cmds[1:]:
                if fmt == "md":
                    print(f"|{md_format(device)}|{md_format(chk_cmd)}|", end="")
                else:
                    print(f"{' ':{COLUMN1}} \033[1m{chk_cmd:{COLUMN2}}\033[0m", end="")
                if not dry_run:
                    if chk_cmd in run_commands:
                        tcmd = TangoCommandInfo(logger, dev, chk_cmd)
                        tcmd.show_value(fmt, prefix, suffix)
                    elif chk_cmd in run_commands_name:
                        tcmd = TangoCommandInfo(logger, dev, chk_cmd, dev.name())
                        tcmd.show_value(fmt, prefix, suffix)
                    else:
                        print(" N/A")
                else:
                    print()
