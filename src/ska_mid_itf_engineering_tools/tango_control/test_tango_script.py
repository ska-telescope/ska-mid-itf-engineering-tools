"""Dance the Tango from a script."""
import json
import logging
import os
from typing import Any, TextIO

import tango


class TangoScript:
    """The classy Tango."""

    def __init__(
        self,
        logger: logging.Logger,
        input_file: str | None,
        device_name: str | None,
        dry_run: bool,
    ) -> int:
        """
        Read actions from file.

        :param input_file: input file
        :param device_name: device name
        :param dry_run: flag for dry run
        :raise: error condition
        """
        self.logger = logger
        # Get Tango database host
        tango_host = os.getenv("TANGO_HOST")
        if device_name is None:
            self.logger.error("Tango device name not set")
            raise Exception("Tango device name not set")
        try:
            self.logger.info("Connect device %s", device_name)
            self.dev: tango.DeviceProxy = tango.DeviceProxy(device_name)
        except tango.ConnectionFailed as terr:
            print(f"[FAILED] {device_name} connection failed")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
            self.dev = None
        except tango.DevFailed as terr:
            print(f"[FAILED] {device_name} device failed")
            print(f"[FAILED] {terr.args[0].desc.strip()}")
            self.logger.debug(terr)
            self.dev = None
        try:
            self.dev_name = self.dev.name()
        except tango.DevFailed:
            self.dev_name = device_name + " (N/A)"
        self.logger.info("Read device name %s", self.dev_name)
        # Read configuration file
        self.logger.warning("Read file %s", input_file)
        cfg_file: TextIO = open(input_file)
        self.cfg_data: Any = json.load(cfg_file)
        cfg_file.close()

    def run(self):
        """Run the thing."""
        self.logger.info("Process : %s", self.cfg_data)
        for test in self.cfg_data:
            test_cfg = self.cfg_data[test]
            if type(test_cfg) is list:
                for thing in test_cfg:
                    if type(thing) is dict:
                        # for key in thing:
                        #     print(f"{key:16} : {thing[key]}")
                        if "attribute" in thing:
                            attr_thing = thing["attribute"]
                            if "read" in thing:
                                attr_read = thing["read"]
                            else:
                                attr_read = None
                            if "write" in thing:
                                attr_write = thing["write"]
                            else:
                                attr_write = None
                            self.read_write_attribute(attr_thing, attr_read, attr_write)
                        elif "command" in thing:
                            cmd_thing = thing["command"]
                            if "args" in thing:
                                cmd_args = thing["args"]
                            else:
                                cmd_args = None
                            self.run_command(cmd_thing, cmd_args)
                    else:
                        self.logger.info(f"Device {self.dev_name} {thing} ({type(thing)})")
            else:
                self.logger.info(f"{test} : {test_cfg}")
        return 0

    def read_write_attribute(
        self,
        attr_thing: str | None,
        attr_read: int | float | str | None,
        attr_write: int | float | str | None,
    ):
        """
        Read or write Tango attribute.

        :param attr_thing: attribute name
        :param attr_read: read value
        :param attr_write: write value
        :return: error condition
        """
        if attr_read is not None:
            self.logger.debug("Read attrbute %s : should be %s", attr_thing, str(attr_read))
            attr_val = self.dev.read_attribute(attr_thing)
            print("Attrbute %s : %s" % (attr_val.name, attr_val.value))
        if attr_write is not None:
            self.logger.info("Write attrbute %s value %s", attr_thing, str(attr_write))
            try:
                self.dev.write_attribute(attr_thing, attr_write)
            except tango.DevFailed as terr:
                self.logger.error("Write failed : %s", terr.args[0].desc.strip())
                return 1
            print("Attrbute %s set to %s" % (attr_val.name, attr_val.value))
        return 0

    def run_command(self, cmd_thing: str, cmd_args: Any) -> int:
        """
        Run Tango command.

        :param cmd_thing: command name
        :param cmd_args: command arguments
        :return: error condition
        """
        if cmd_args is None:
            self.logger.info("Run command %s", cmd_thing)
            cmd_val = self.dev.command_inout(cmd_thing)
            print("Command %s : %s" % (cmd_thing, cmd_val))
        else:
            self.logger.info("Run command %s arguments %s", cmd_thing, cmd_args)
            cmd_val = self.dev.command_inout(cmd_thing, cmd_args)
            print("Command %s (%s) : %s" % (cmd_thing, cmd_args, cmd_val))
        return 0
