"""Read and display Tango stuff."""
import logging
from typing import Any

from ska_mid_itf_engineering_tools.tango_control.read_tango_device import TangoctlDeviceBasic


class TangoctlDeviceConfig(TangoctlDeviceBasic):
    """Read all the configuration on offer."""

    commands: dict = {}
    attributes: dict = {}
    properties: dict = {}

    def __init__(
        self,
        logger: logging.Logger,
        device: str,
    ):
        """
        Get it on.

        :param logger: logging handle
        :param device: device name
        """
        super().__init__(logger, device)
        cmds = sorted(self.dev.get_command_list())
        attribs = sorted(self.dev.get_attribute_list())
        for attrib in attribs:
            self.logger.debug("Add attribute %s", attrib)
            self.attributes[attrib] = {}
            self.attributes[attrib]["config"] = self.dev.get_attribute_config(attrib)
        for cmd in cmds:
            self.logger.debug("Add command %s", cmd)
            self.commands[cmd] = {}
            self.commands[cmd]["config"] = self.dev.get_command_config(cmd)
        props = sorted(self.dev.get_property_list("*"))
        for prop in props:
            self.logger.debug("Add property %s", prop)
            self.properties[prop] = {}
        self.info: Any = self.dev.info()

    def get_json(self, delimiter: str) -> dict:
        """
        Convert internal values to JSON.

        :param delimiter: field are seperated by this
        :return: dictionary
        """

        def set_json_attribute() -> None:
            """Add attributes to dictionary."""
            devdict["attributes"][attrib] = {}
            devdict["attributes"][attrib]["config"] = {}
            devdict["attributes"][attrib]["config"]["description"] = self.attributes[attrib][
                "config"
            ].description
            devdict["attributes"][attrib]["config"]["root_attr_name"] = self.attributes[attrib][
                "config"
            ].root_attr_name
            devdict["attributes"][attrib]["config"]["format"] = self.attributes[attrib][
                "config"
            ].format
            devdict["attributes"][attrib]["config"]["data_format"] = str(
                self.attributes[attrib]["config"].data_format
            )
            devdict["attributes"][attrib]["config"]["disp_level"] = str(
                self.attributes[attrib]["config"].disp_level
            )
            devdict["attributes"][attrib]["config"]["data_type"] = str(
                self.attributes[attrib]["config"].data_type
            )
            devdict["attributes"][attrib]["config"]["display_unit"] = self.attributes[attrib][
                "config"
            ].display_unit
            devdict["attributes"][attrib]["config"]["standard_unit"] = self.attributes[attrib][
                "config"
            ].standard_unit
            devdict["attributes"][attrib]["config"]["writable"] = str(
                self.attributes[attrib]["config"].writable
            )
            devdict["attributes"][attrib]["config"]["writable_attr_name"] = self.attributes[
                attrib
            ]["config"].writable_attr_name

        devdict: dict = {}
        devdict["name"] = self.dev_name
        devdict["version"] = self.version
        devdict["versioninfo"] = self.dev.getversioninfo()
        devdict["adminMode"] = str(self.dev.adminMode).split(".")[1]
        devdict["info"] = {}
        devdict["info"]["dev_class"] = self.info.dev_class
        devdict["info"]["server_host"] = self.info.server_host
        devdict["info"]["server_id"] = self.info.server_id
        devdict["attributes"] = {}
        for attrib in self.attributes:
            self.logger.debug("Set attribute %s", attrib)
            set_json_attribute()

        self.logger.info("INFO: %s", devdict)
        return devdict
