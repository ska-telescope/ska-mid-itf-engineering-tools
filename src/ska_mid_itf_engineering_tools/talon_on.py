"""This script turns on the TalonDx using CSP On command."""

import logging
import sys

# import os
import json
import time

from ska_ser_logging import configure_logging
from tango import DeviceProxy, DevState

TIMEOUT = 60


def main():  # noqa C901
    """Call the CBF On command."""
    configure_logging(logging.DEBUG)
    logger = logging.getLogger(__name__)

    CSP = DeviceProxy("mid-csp/control/0")
    CSPSubarray = DeviceProxy("mid-csp/subarray/01")

    CBF = DeviceProxy("mid_csp_cbf/sub_elt/controller")
    CBFSubarray = DeviceProxy("mid_csp_cbf/sub_elt/subarray_01")

    # Exit if CSP is already ON
    if CSP.State() == DevState.ON and CSP.adminmode == 0:
        logger.info("CSP is already ON")
        return

    if CSP.adminmode != 0:
        logger.info("Setting CSP adminmode to ONLINE")
        CBF.adminmode = 0
        while CBF.State() != DevState.OFF:
            logger.info(f"Waiting for CBF to change state from {CBF.State()} to OFF")
            time.sleep(1)
        CSP.adminmode = 0
        while (
            CSP.adminmode != 0
            or CSPSubarray.State() != DevState.OFF
            or CBFSubarray.State() != DevState.OFF
        ):
            if CSP.adminmode != 0:
                logger.info(f"Waiting for CSP to change adminmode from {CSP.adminmode} to ONLINE")
                logger.info(f"Hoping CSP will change state from {CSP.State()} to OFF")
            if CSPSubarray.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CSP Subarray to change state from {CSPSubarray.State()} to OFF"
                )
            if CBFSubarray.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CBF Subarray to change state from {CBFSubarray.State()} to OFF"
                )
            time.sleep(1)
        logger.info(f"CSP adminmode is now {CSP.adminmode}")
        logger.info(f"CSP State is now {CSP.State()}")
        logger.info(f"CSP Subarray State is now {CSPSubarray.State()}")
        logger.info(f"CBF Subarray State is now {CBFSubarray.State()}")

    dish_config = {
        "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
        "dish_parameters": {
            "SKA001": {"vcc": 1, "k": 11},
            "SKA036": {"vcc": 2, "k": 101},
            "SKA063": {"vcc": 3, "k": 1127},
            "SKA100": {"vcc": 4, "k": 620},
        },
    }  # with open(
    #     os.path.join(
    #         os.path.dirname(__file__), "..", "..", "resources", "data", "init_sys_param.json"
    #     ),
    #     "r",
    # ) as f:
    #     dish_config = json.load(f)
    CSP.loaddishcfg(json.dumps(dish_config))

    if CSP.State() == DevState.FAULT:
        logger.info("CSP is in FAULT state. Exiting.")
        sys.exit(1)

    # Next set simulation to false - hardware use!
    CBF.simulationMode = False
    logger.info(f"CBF simulationMode is now {CBF.simulationMode}")

    # Timeout for long-running command
    CBF.commandTimeout = TIMEOUT
    logger.info("Turning CSP ON - this may take a while...")
    CBF.on([])
    k = 1
    while CBF.State() != DevState.ON:

        def fib(n):
            return n if n <= 1 else fib(n - 1) + fib(n - 2)

        logger.info(
            f"Waiting for CBF to change state from {CBF.State()} to ON for {fib(k)} seconds"
        )
        time.sleep(fib(k))
        k += 1
    logger.info("CBF is ON")
    return


if __name__ == "__main__":
    main()
