"""This script turns on the TalonDx using CSP On command."""

import logging
import sys
import time

from ska_ser_logging import configure_logging
from tango import DeviceProxy, DevState

TIMEOUT = 60


def main():
    """Call the CBF On command."""
    configure_logging(logging.DEBUG)
    logger = logging.getLogger(__name__)
    CBF = DeviceProxy(
        "mid_csp_cbf/sub_elt/controller"
    )  # This is a direct call on the CBF MCS, not via the CSP.
    CSP = DeviceProxy("mid-csp/control/0")
    CSPSubarray = DeviceProxy("mid-csp/subarray/01")
    CBFSubarray = DeviceProxy("mid_csp_cbf/sub_elt/subarray_01")

    # Exit if CSP is already ON
    if CSP.State() == DevState.ON and CSP.adminmode == 0:
        logger.info("CSP is already ON")
        return

    if CSP.adminmode != 0:
        logger.info("Setting CSP adminmode to ONLINE")
        CSP.adminmode = 0
        while (
            CSP.adminmode != 0
            or CSPSubarray.State() != DevState.OFF
            or CBFSubarray.State() != DevState.OFF
        ):
            if CSP.adminmode != 0:
                logger.info(f"Waiting for CSP to change adminmode from {CSP.adminmode} to ONLINE")
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

    if CSP.State() == DevState.FAULT:
        logger.info("CSP is in FAULT state. Exiting.")
        sys.exit(1)

    # Next set simulation to false - hardware use!
    CBF.simulationMode = False
    logger.info(f"CBF simulationMode is now {CBF.simulationMode}")

    # Timeout for long-running command
    CSP.commandTimeout = TIMEOUT
    logger.info("Turning CSP ON - this may take a while...")
    CSP.on([])
    k = 1
    while CSP.State() != DevState.ON:
        logger.info(f"Waiting for CSP to change state from {CSP.State()} to ON for {k} seconds")

        def fib(n):
            return n if n <= 1 else fib(n - 1) + fib(n - 2)

        time.sleep(fib(k))
        k += 1
    logger.info("CSP is ON")
    return


if __name__ == "__main__":
    main()
