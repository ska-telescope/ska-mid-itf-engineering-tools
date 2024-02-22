"""Read and display Tango properties."""
import logging
import os

import tango

from ska_mid_itf_engineering_tools.tango_info.get_tango_devices import list_devices


def show_properties(
    logger: logging.Logger,
    cfg_data: dict,
    disp_action: int,
    evrythng: bool,
    p_name: str | None,
    dry_run: bool,
) -> None:
    """
    Display information about Tango devices.

    :param logger: logging handle
    :param cfg_data: configuration in JSON format
    :param disp_action: flag for markdown output
    :param evrythng: get commands and attributes regadrless of state
    :param p_name: filter command name
    :param dry_run: do not display values
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

    if not dry_run:
        print(f"{'DEVICE':48} {'PROPERTY':40} VALUE")
    else:
        print(f"{'DEVICE':48} PROPERTY")

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
            print(f"{dev.name():48}", end="")
            print(f" \033[1m{props_found[0]}\033[0m")
            for prop in props_found[1:]:
                print(f"{' ':48} \033[1m{prop}\033[0m")
