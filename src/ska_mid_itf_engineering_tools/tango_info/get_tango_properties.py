"""Read and display Tango properties."""

import logging
import os
from typing import Any

import tango

from ska_mid_itf_engineering_tools.tango_info.get_tango_devices import (
    COLUMN1,
    COLUMN2,
    list_devices,
    md_format,
)


class TangoPropertyInfo:
    """Read attribute value."""

    def __init__(self, logger: logging.Logger, dev: Any, prop_name: str):
        """
        Print attribute value.

        :param logger: logging handle
        :param dev: Tango device handle
        :param prop_name: attribute name
        """
        self.attrib_value: Any
        self.data_format: Any

        self.logger = logger
        self.prop_name = prop_name
        self.dev = dev
        self.prop_values = self.dev.get_property(self.prop_name)
        self.prop_value = self.prop_values[self.prop_name]
        self.logger.info(
            "Device %s property %s value %s", self.dev.name(), self.prop_name, self.prop_value
        )

    def _show_value_txt(self, prefix: str) -> None:
        """
        Print attribute value.

        :param prefix: prefix for printing
        """
        prop_list = self.prop_value
        if len(prop_list) == 1:
            print(f" {prop_list[0]}")
        elif len(prop_list[0]) > 30 and len(prop_list[1]) > 30:
            prop_val = prop_list[0]
            print(f" {prop_val}")
            for prop_val in prop_list[1:]:
                print(f"{prefix} {prop_val}")
        else:
            print(f" {prop_list[0]}  {prop_list[1]}")
            n = 2
            while n < len(prop_list):
                print(f"{prefix} {prop_list[n]}  {prop_list[n+1]}")
                n += 2

    def _show_value_md(self, prefix: str, suffix: str) -> None:
        """
        Print attribute value.

        :param prefix: prefix for printing
        :param suffix: suffix for printing
        """
        prop_list = self.prop_value
        if len(prop_list) == 1:
            print(f"{md_format(prop_list[0])}{suffix}")
        elif len(prop_list[0]) > 30 and len(prop_list[1]) > 30:
            prop_val = prop_list[0]
            print(f"{md_format(prop_val)}{suffix}")
            for prop_val in prop_list[1:]:
                print(f"{prefix}{md_format(prop_val)}{suffix}")
        else:
            print(f"{md_format(prop_list[0])}  {md_format(prop_list[1])}{suffix}")
            n = 2
            while n < len(prop_list):
                print(f"{prefix}{md_format(prop_list[n])}  {md_format(prop_list[n+1])}{suffix}")
                n += 2

    def show_value(self, fmt: str, prefix: str, suffix: str) -> None:
        """
        Show the value of the thing.

        :param fmt: output format
        :param prefix: put in front
        :param suffix: add at the back
        """
        if fmt == "md":
            self._show_value_md(prefix, suffix)
        else:
            self._show_value_txt(prefix)


def show_properties(  # noqa: C901
    logger: logging.Logger,
    cfg_data: dict,
    disp_action: int,
    evrythng: bool,
    p_name: str | None,
    dry_run: bool,
    fmt: str,
) -> None:
    """
    Display information about Tango devices.

    :param logger: logging handle
    :param cfg_data: configuration in JSON format
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param p_name: filter command name
    :param dry_run: do not display values
    :param fmt: output format
    """
    logger.info("Read properties matching %s", p_name)
    if p_name is None:
        return

    # Get Tango database host
    tango_host = os.getenv("TANGO_HOST")
    logger.info("Tango host %s" % tango_host)

    # Read devices
    device_list = list_devices(logger, cfg_data, evrythng, None)
    logger.info("Read %d devices" % (len(device_list)))

    prefix: str
    suffix: str
    if fmt == "md":
        if not dry_run:
            print("|DEVICE NAME|PROPERTY|VALUE|")
            print("|:----------|:-------|:----|")
        else:
            print("|DEVICE NAME|PROPERTY|")
            print("|:----------|:-------|")
        prefix = "|||"
        suffix = "|"
    else:
        if not dry_run:
            print(f"{'DEVICE NAME':{COLUMN1}} {'PROPERTY':{COLUMN2}} VALUE")
        else:
            print(f"{'DEVICE NAME':{COLUMN1}} PROPERTY")
        prefix = " " * (COLUMN1 + COLUMN2 + 1)
        suffix = ""

    p_name = p_name.lower()
    for device in sorted(device_list):
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        prop_list = dev.get_property_list("*")
        props_found = []
        for prop in prop_list:
            # TODO implement minimum string length
            if p_name in prop.lower():
                props_found.append(prop)
        if props_found:
            prop = props_found[0]
            logger.info("Matched device %s property %s", device, prop)
            if fmt == "md":
                print(f"|{md_format(dev.name())}|{md_format(prop)}|", end="")
            else:
                print(f"{dev.name():{COLUMN1}} \033[1m{prop:{COLUMN2}}\033[0m", end="")
            if not dry_run:
                tprop = TangoPropertyInfo(logger, dev, prop)
                tprop.show_value(fmt, prefix, suffix)
            else:
                print()
            for prop in props_found[1:]:
                logger.info("Matched device %s property %s", device, prop)
                if fmt == "md":
                    print(f"||{md_format(prop)}|", end="")
                else:
                    print(f"{' ':{COLUMN1}} \033[1m{prop:{COLUMN2}}\033[0m", end="")
                if not dry_run:
                    tprop = TangoPropertyInfo(logger, dev, prop)
                    tprop.show_value(fmt, prefix, suffix)
                else:
                    print()
