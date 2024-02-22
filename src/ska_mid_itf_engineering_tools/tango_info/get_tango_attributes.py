"""Read Tango attribute values."""
import json
import logging
import os
from typing import Any

import numpy
import tango

from ska_mid_itf_engineering_tools.tango_info.get_tango_devices import list_devices


class TangoAttributeInfo:
    """Read attribute value."""

    def __init__(self, logger: logging.Logger, dev: Any, attrib_name: str):
        """
        Print attribute value.

        :param logger: logging handle
        :param dev: Tango device handle
        :param attrib_name: attribute name
        :return: attribute value
        """
        self.attrib_value: Any
        self.data_format: Any

        self.logger = logger
        self.attrib_name = attrib_name
        self.dev = dev
        try:
            self.attrib_value = self.dev.read_attribute(self.attrib_name).value
        except tango.DevFailed as terr:
            self.attrib_value = f"<ERROR> \033[3m{terr.args[0].desc.strip()}\033[0m"
        except Exception:
            self.attrib_value = None
        attrib_cfg = self.dev.get_attribute_config(self.attrib_name)
        self.data_format = attrib_cfg.data_format

    def get_value(self) -> Any:
        """Get value"""
        return self.attrib_value

    def _show_attribute_value_scalar(self, prefix: str) -> None:  # noqa: C901
        """
        Print attribute scalar value.

        :param prefix: data prefix string
        """
        json_fmt = True
        try:
            attrib_json = json.loads(self.attrib_value)
        except Exception:
            json_fmt = False
        self.logger.debug("Scalar %s : %s", type(self.attrib_value), self.attrib_value)
        if not json_fmt:
            attrib_value = str(self.attrib_value)
            if "\n" in attrib_value:
                attrib_values = attrib_value.split("\n")
                print(f" '{attrib_values[0]}'")
                for attrib_val in attrib_values[1:]:
                    print(f"{prefix} '{attrib_val.strip()}'")
            else:
                print(f" '{attrib_value}'")
            return
        # print(" <JSON>")
        if type(attrib_json) is dict:
            if not attrib_json:
                print(" <EMPTY>")
                return
            n = 0
            for value in attrib_json:
                print("")
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
                n += 1
        elif type(attrib_json) is list:
            print(f" {self.attrib_value[0]}")
            for attrib_val in self.attrib_value[1:]:
                print(f"{prefix+'     '} {attrib_val}")
        elif type(self.attrib_value) is str:
            print(f" {self.attrib_value}")
        else:
            print(f" '{self.attrib_value}' (type {type(self.attrib_value)})")

    def _show_attribute_value_spectrum(self, prefix: str) -> None:  # noqa: C901
        """
        Print attribute spectrum value.

        :param prefix: data prefix string
        """
        self.logger.debug("Spectrum %s : %s", type(self.attrib_value), self.attrib_value)
        if type(self.attrib_value) is dict:
            if self.attrib_value:
                int_models = json.loads(self.attrib_value)  # type: ignore[arg-type]
                for key in int_models:
                    print(f"{prefix}   {key}")
                    int_model_values = int_models[key]
                    if type(int_model_values) is dict:
                        for value in int_model_values:
                            print(f"{prefix+'     '} {value} : {int_model_values[value]}")
                    else:
                        print(f"{prefix+'     '} {value} : {int_model_values}")
            else:
                print(" {}")
        elif type(self.attrib_value) is tuple:
            if self.attrib_value:
                a_val = self.attrib_value[0]
                if not a_val:
                    a_val = "''"
                print(f" {a_val}")
                for a_val in self.attrib_value[1:]:
                    if not a_val:
                        a_val = "''"
                    print(f"{prefix} {a_val}")
            else:
                print(" ()")
        elif type(self.attrib_value) is list:
            if self.attrib_value:
                print(f" {self.attrib_value[0]}")
                for attrib_val in self.attrib_value[1:]:
                    print(f"{prefix+'     '} {attrib_val}")
            else:
                print(" []")
        elif type(self.attrib_value) is numpy.ndarray:
            a_list = self.attrib_value.tolist()
            if a_list:
                print(f" {a_list[0]}")
                for a_val in a_list[1:]:
                    print(f"{prefix} {a_val}")
            else:
                print(" []")
        elif type(self.attrib_value) is str:
            print(f" {self.attrib_value}")
        elif self.attrib_value is None:
            print(" N/A")
        else:
            print(f" {type(self.attrib_value)}:{self.attrib_value}")

    def _show_attribute_value_other(self, prefix: str) -> None:
        attrib_value = self.attrib_value
        self.logger.debug("Attribute value %s : %s", type(attrib_value), attrib_value)
        if type(attrib_value) is numpy.ndarray:
            a_list = attrib_value.tolist()
            if a_list:
                print(f" {a_list[0]}")
                for a_val in a_list[1:]:
                    print(f"{prefix} {a_val}")
            else:
                print(" []")
        elif type(attrib_value) is tuple:
            if attrib_value:
                print(f" {attrib_value[0]}")
                for attrib_val in attrib_value[1:]:
                    print(f"{prefix} {attrib_val}")
            else:
                print(" ()")
        else:
            print(f" {attrib_value}")

    def show_value(self, prefix: str) -> None:  # noqa: C901
        """
        Print attribute value.

        :param attrib: attribute name
        :param prefix: data prefix string
        """
        if self.attrib_value is None:
            print(" N/A")
        else:
            # pylint: disable-next=c-extension-no-member
            if self.data_format == tango._tango.AttrDataFormat.SCALAR:
                self._show_attribute_value_scalar(prefix)
            # pylint: disable-next=c-extension-no-member
            elif self.data_format == tango._tango.AttrDataFormat.SPECTRUM:
                self._show_attribute_value_spectrum(prefix)
            else:
                self._show_attribute_value_other(prefix)


def show_attributes(  # noqa: C901
    logger: logging.Logger,
    cfg_data: dict,
    disp_action: int,
    evrythng: bool,
    a_name: str | None,
    dry_run: bool,
) -> None:
    """
    Display information about Tango devices.

    :param logger: logging handle
    :param cfg_data: configuration in JSON format
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param a_name: filter attribute name
    :param dry_run: do not display values
    """
    prefix: str = " " * 89

    logger.info("Read attributes matching %s", a_name)
    if a_name is None:
        return

    # Get Tango database hist
    tango_host = os.getenv("TANGO_HOST")
    logger.info("Tango host %s" % tango_host)

    # Read devices
    device_list = list_devices(logger, cfg_data, evrythng, None)
    logger.info(f"{len(device_list)} devices available")

    logger.info("Read %d devices" % (len(device_list)))
    if disp_action == 2:
        print("# Tango devices")
        print("## Tango host\n```\n%s\n```" % tango_host)
        print(f"## Number of devices\n{len(device_list)}")

    if not dry_run:
        print(f"{'DEVICE':48} {'ATTRIBUTE':40} VALUE")
    else:
        print(f"{'DEVICE':48} ATTRIBUTE")
    a_name = a_name.lower()
    for device in sorted(device_list):
        dev: tango.DeviceProxy = tango.DeviceProxy(device)
        try:
            attribs = sorted(dev.get_attribute_list())
        except Exception:
            attribs = []
        # Check attribute names
        attribs_found = []
        for attrib_name in sorted(attribs):
            # TODO implement minimum string length
            if a_name in attrib_name.lower():
                attribs_found.append(attrib_name)
        if attribs_found:
            print(f"{device:48}", end="")
            attrib_name = attribs_found[0]
            print(f" \033[1m{attrib_name:40}\033[0m", end="")
            if not dry_run:
                attrib_val = TangoAttributeInfo(logger, dev, attrib_name)
                attrib_val.show_value(prefix)
            else:
                print()
            for attrib_name in attribs_found[1:]:
                print(f"{' ':48} \033[1m{attrib_name:40}\033[0m", end="")
                if not dry_run:
                    attrib_val = TangoAttributeInfo(logger, dev, attrib_name)
                    attrib_val.show_value(prefix)
                else:
                    print()
