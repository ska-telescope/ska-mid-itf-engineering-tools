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
        input_file: int | str | bytes | os.PathLike[str] | os.PathLike[bytes],
        device_name: str | None,
        dry_run: bool,
    ):
        """
        Read actions from file.

        :raises Exception: error condition
        :param logger: logging handle
        :param input_file: input file
        :param device_name: device name
        :param dry_run: flag for dry run
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
            print(f"[FAILED] {device_name} connection to {tango_host} failed")
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
        self.attributes = sorted(self.dev.get_attribute_list())
        self.commands = sorted(self.dev.get_command_list())
        self.properties = sorted(self.dev.get_property_list("*"))

    def run(self) -> int:
        """
        Run the thing.

        :return: error condition
        """
        self.logger.info("Process : %s", self.cfg_data)
        for test in self.cfg_data:
            test_cfg = self.cfg_data[test]
            if type(test_cfg) is list:
                for thing in test_cfg:
                    if type(thing) is dict:
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
    ) -> int:
        """
        Read or write Tango attribute.

        :param attr_thing: attribute name
        :param attr_read: read value
        :param attr_write: write value
        :return: error condition
        """
        if attr_thing not in self.attributes:
            self.logger.error("Device does not have a '%s' attribute", attr_thing)
            return 1
        if attr_read is not None:
            self.logger.debug("Read attribute %s : should be '%s'", attr_thing, str(attr_read))
            attrib_data = self.dev.read_attribute(attr_thing)
            print("Attribute %s : %s" % (attrib_data.name, attrib_data.value))
        if attr_write is not None:
            attrib_data = self.dev.read_attribute(attr_thing)
            attr_type = str(attrib_data.type)
            if type(attr_write) is str:
                if "${" in attr_write and "}" in attr_write:
                    env_name = attr_write.split("{")[1].split("}")[0]
                    attr_write = os.getenv(env_name)
                    self.logger.info("Read environment variable %s : %s", env_name, attr_write)
            self.logger.info("Write attrbute %s value %s", attr_thing, str(attr_write))
            write_val: Any
            if attr_type == "DevEnum":
                write_val = int(attr_write)  # type: ignore[arg-type]
            else:
                write_val = str(attr_write)
            try:
                self.dev.write_attribute(attr_thing, write_val)
            except tango.DevFailed as terr:
                self.logger.error("Write failed : %s", terr.args[0].desc.strip())
                return 1
            attrib_data = self.dev.read_attribute(attr_thing)
            print("Attrbute %s set to %s" % (attrib_data.name, attrib_data.value))
        return 0

    def run_command(self, cmd_thing: str, cmd_args: Any) -> int:
        """
        Run Tango command.

        :param cmd_thing: command name
        :param cmd_args: command arguments
        :return: error condition
        """
        if cmd_thing not in self.commands:
            self.logger.error("Device does not have a '%s' command", cmd_thing)
            return 1
        if cmd_args is None:
            self.logger.info("Run command %s", cmd_thing)
            cmd_val = self.dev.command_inout(cmd_thing)
            print("Command %s : %s" % (cmd_thing, cmd_val))
        else:
            self.logger.info("Run command %s arguments %s", cmd_thing, cmd_args)
            cmd_val = self.dev.command_inout(cmd_thing, cmd_args)
            print("Command %s (%s) : %s" % (cmd_thing, cmd_args, cmd_val))
        return 0
