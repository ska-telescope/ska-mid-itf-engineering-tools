"""Read and display Tango commands."""
import logging
import os
from typing import Any

import tango

from ska_mid_itf_engineering_tools.tango_info.get_tango_devices import list_devices


def show_commands(  # noqa: C901
    logger: logging.Logger,
    cfg_data: dict,
    disp_action: int,
    evrythng: bool,
    c_name: str | None,
    dry_run: bool,
) -> None:
    """
    Display information about Tango devices.

    :param logger: logging handle
    :param cfg_data: configuration in JSON format
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param c_name: filter command name
    :param dry_run: do not display values
    """

    def get_command_inout(prefix: str, idev: Any, cmd: str, args: Any = None) -> Any:
        """
        Run command and get output.

        :param prefix: print at front of line
        :param idev: Tango device handle
        :param cmd: command name
        :param args: arguments for command
        """
        try:
            if args:
                inout = idev.command_inout(cmd, args)
            else:
                inout = idev.command_inout(cmd)
        except tango.DevFailed as terr:
            return f"<ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m"
        if type(inout) is list:
            if inout:
                inout = str(inout[0])
            else:
                inout = "[]"
        else:
            inout = str(inout)
        if "\n" in inout:
            ios = str(inout).split("\n")
            rval = ios[0]
            for io in ios[1:]:
                rval += f"\n{prefix} {io.strip()}"
        else:
            rval = inout
        return rval

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

    if not dry_run:
        print(f"{'DEVICE':48} {'COMMAND':40} VALUE")
    else:
        print(f"{'DEVICE':48} COMMAND")

    run_commands = cfg_data["run_commands"]
    logger.info("Run commands %s", run_commands)
    run_commands_name = cfg_data["run_commands_name"]
    logger.info("Run commands with name %s", run_commands_name)
    min_str_len = cfg_data["min_str_len"]

    # Read devices
    device_list = list_devices(logger, cfg_data, evrythng, None)
    logger.info("Read %d devices" % (len(device_list)))

    prefix = " " * 89
    for device in sorted(device_list):
        logger.info("Check device %s", device)
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        chk_cmds = filter_command(dev, c_name, min_str_len)
        if chk_cmds:
            print(f"{device:48}", end="")
            chk_cmd = chk_cmds[0]
            print(f" \033[1m{chk_cmd:40}\033[0m", end="")
            if chk_cmd in run_commands:
                cmd_io = get_command_inout(prefix, dev, chk_cmd)
            elif chk_cmd in run_commands_name:
                cmd_io = get_command_inout(prefix, dev, chk_cmd, dev.name())
            else:
                cmd_io = "N/A"
            print(f" {cmd_io}")
            for chk_cmd in chk_cmds[1:]:
                print(f"{' ':48} \033[1m{chk_cmd:40}\033[0m", end="")
                if chk_cmd in run_commands:
                    cmd_io = get_command_inout(prefix, dev, chk_cmd)
                elif chk_cmd in run_commands_name:
                    cmd_io = get_command_inout(prefix, dev, chk_cmd, dev.name())
                else:
                    cmd_io = "N/A"
                print(f" {cmd_io}")
