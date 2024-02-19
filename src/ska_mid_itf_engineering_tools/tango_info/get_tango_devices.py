"""Compile a list of Tango devices."""
import logging
import os
import tango
from typing import Any


class TangoDevices:
    """Compile a list of available Tango devices."""

    def __init__(self, logger: logging.Logger, evrythng: bool, cfg_data: Any):
        """
        Read Tango device names.

        :return: list of devices
        """
        self.logger = logger
        self.tango_devices: list = []
        # Connect to database
        try:
            database = tango.Database()
        except Exception:
            tango_host = os.getenv("TANGO_HOST")
            print("[FAILED] Could not connect to Tango database %s", tango_host)
        # Read devices
        device_list = database.get_device_exported("*")
        print(f"[  OK  ] {len(device_list)} devices available")

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
            self.logger.debug("Add device %s", device)
            self.tango_devices.append(device)

        self.logger.info("Found %d devices", len(self.tango_devices))
        self.min_str_len = cfg_data["min_str_len"]

    def list_devices(self) -> list:
        """
        Get list of devices.

        :return: list of devices
        """
        return self.tango_devices

    def check_command(self, dev: Any, c_name: str | None) -> list:
        """
        Read commands from database.

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
        self.logger.info("Check commands %s", cmds)
        c_name = c_name.lower()
        if len(c_name) <= self.min_str_len:
            for cmd in sorted(cmds):
                if c_name == cmd.lower():
                    cmds_found.append(cmd)
        else:
            for cmd in sorted(cmds):
                if c_name in cmd.lower():
                    cmds_found.append(cmd)
        return cmds_found

    def show_commands(self, c_name: str | None) -> dict:
        """
        Filter by command name.

        :param c_name: command name
        """
        dev_cmds = {}
        for device in sorted(self.tango_devices):
            dev: tango.DeviceProxy = tango.DeviceProxy(device)
            dev_name = dev.name()
            chk_cmds = self.check_command(dev, c_name)
            if chk_cmds:
                dev_cmds[dev_name] = chk_cmds
        return dev_cmds
