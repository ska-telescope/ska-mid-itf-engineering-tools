"""This script turns on the TalonDx using CSP On command."""

import json
import logging
import os
import sys
import time
from typing import Any

from ska_ser_logging import configure_logging  # type: ignore
from tango import DeviceProxy, DevState

TIMEOUT = 100
ns = os.environ["KUBE_NAMESPACE"]
mcs_config_pth = os.path.join(os.getcwd(), os.environ["MCS_CONFIG_FILE_PATH"])
hw_config_src_pth = os.path.join(mcs_config_pth, "hw_config.yaml")
hw_config_dest_pth = ns + "/ds-cbfcontroller-controller-0:/app/mnt/hw_config/hw_config.yaml"
configure_logging(logging.DEBUG)
logger = logging.getLogger(__name__)


def wait_for_devices(
    cbf: Any,
    csp: Any,
    csp_subarray1: Any,
    csp_subarray2: Any,
    csp_subarray3: Any,
    cbf_subarray1: Any,
    cbf_subarray2: Any,
    cbf_subarray3: Any,
) -> None:
    """Wait for Tango Deviceproxies to change states.

    :param cbf : tango.DeviceProxy CBF Controller DeviceProxy
    :param csp : tango.DeviceProxy CSP Controller DeviceProxy
    :param csp_subarray1 : tango.DeviceProxy Subarray DeviceProxy
    :param csp_subarray2 : tango.DeviceProxy Subarray DeviceProxy
    :param csp_subarray3 : tango.DeviceProxy Subarray DeviceProxy
    :param cbf_subarray1 : tango.DeviceProxy Subarray DeviceProxy
    :param cbf_subarray2 : tango.DeviceProxy Subarray DeviceProxy
    :param cbf_subarray3 : tango.DeviceProxy Subarray DeviceProxy
    """
    READY = False
    timer = 0
    while not READY:
        time.sleep(1)
        timer += 1
        if timer == 30:
            break
        device_proxies = [
            csp,
            cbf,
            cbf_subarray1,
            cbf_subarray2,
            cbf_subarray3,
            csp_subarray1,
            csp_subarray2,
            csp_subarray3,
        ]

        for dp in device_proxies:
            state = dp.State()
            server = dp.name()
            adminmode = dp.adminmode
            if state != DevState.OFF or (
                server in ["mid-csp/contro/0", "mid_csp_cbf/sub_elt/controller"] and adminmode != 0
            ):
                logger.info(
                    f"Waiting for {server} to change state from "
                    f"{state} to OFF while Adminmode is {adminmode.name}"
                )
                READY = False
                break
            else:
                READY = True
                device_str = f"Device {server}: "
                state_str = f"State {state}; "
                mode_str = f"Adminmode {adminmode.name}."
                logger.info(f"{device_str : <42}{state_str : <15}{mode_str : <20}")
    return


def main() -> None:  # noqa C901
    """Call the CBF On command."""
    logger.debug(f"Path of hw_config.yaml is {hw_config_src_pth}")
    logger.debug(f"Destination Path of hw_config.yaml is {hw_config_dest_pth}")

    cbf = DeviceProxy("mid_csp_cbf/sub_elt/controller")
    csp = DeviceProxy("mid-csp/control/0")
    csp_subarray1 = DeviceProxy("mid-csp/subarray/01")
    csp_subarray2 = DeviceProxy("mid-csp/subarray/02")
    csp_subarray3 = DeviceProxy("mid-csp/subarray/03")
    cbf_subarray1 = DeviceProxy("mid_csp_cbf/sub_elt/subarray_01")
    cbf_subarray2 = DeviceProxy("mid_csp_cbf/sub_elt/subarray_02")
    cbf_subarray3 = DeviceProxy("mid_csp_cbf/sub_elt/subarray_03")

    # Exit if CSP is already ON
    if csp.State() == DevState.ON and csp.adminmode == 0:
        logger.info("CSP is already ON")
        return

    if csp.adminmode != 0:
        logger.info("Setting CSP adminmode to ONLINE")
        csp.adminmode = 0
        wait_for_devices(
            cbf,
            csp,
            csp_subarray1,
            csp_subarray2,
            csp_subarray3,
            cbf_subarray1,
            cbf_subarray2,
            cbf_subarray3,
        )

    filepath = os.path.join(hw_config_src_pth, "init_sys_param.json.json")
    with open(filepath) as fn:
        dish_config = json.load(fn)
        logger.debug(f"Dish Config loaded: {dish_config}")

    # dish_config = {
    #     "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
    #     "dish_parameters": {
    #         "SKA001": {"vcc": 1, "k": 11},
    #         "SKA036": {"vcc": 2, "k": 101},
    #         "SKA063": {"vcc": 3, "k": 1127},
    #         "SKA100": {"vcc": 4, "k": 620},
    #     },
    # }

    csp.loaddishcfg(json.dumps(dish_config))
    vcc_config = csp.dishVccConfig
    logger.debug(f"CSP Controller dishVccConfig is now {vcc_config}")

    # Next set simulation to false - hardware use!
    cbf.simulationMode = False
    cbf_sim_mode = cbf.simulationMode
    while cbf_sim_mode != 0:
        logger.info("Waiting for CBF to change simulationMode to False")
        time.sleep(1)
        cbf_sim_mode = cbf.simulationMode
    logger.info("CBF simulationMode is now False")

    # Timeout for long-running command
    csp.commandTimeout = TIMEOUT
    logger.debug(f"commandTimeout simply set to {TIMEOUT * 1000}")

    csp.set_timeout_millis(TIMEOUT * 1000)
    logger.debug(f"Sent set_timeout_millis({TIMEOUT * 1000}) command")

    logger.info("Turning CSP ON - this may take a while...")
    csp.on([])
    k = 0
    while k < 10:
        logger.warning(f"Sleeping for {TIMEOUT-k*10} seconds while CBF is turning on.")
        time.sleep(10)
        k += 1
    k = 1
    while cbf.State() != DevState.ON:
        if k == 5:
            logger.error("Could not turn the CBF Controller on. Exiting.")
            sys.exit(1)

        def fib(n: int) -> int:
            return n if n <= 1 else fib(n - 1) + fib(n - 2)

        logger.info(
            f"Waiting for CBF to change state from {cbf.State()} to ON "
            "for another {fib(k)} seconds"
        )
        time.sleep(fib(k))
        k += 1
    logger.info("CBF is ON")
    return


if __name__ == "__main__":
    main()
