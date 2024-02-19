"""This script turns on the TalonDx using CSP On command."""

import json
import logging
import os
import sys
import time

from ska_ser_logging import configure_logging  # type: ignore
from tango import DeviceProxy, DevState

TIMEOUT = 100
ns = os.environ["KUBE_NAMESPACE"]
src_pth = os.path.join(os.getcwd(), os.environ["MCS_CONFIG_FILE_PATH"], "hw_config.yaml")
dest_pth = ns + "/ds-cbfcontroller-controller-0:/app/mnt/hw_config/hw_config.yaml"
configure_logging(logging.DEBUG)
logger = logging.getLogger(__name__)


def wait_for_devices(
    CBF, CSP, CSPSubarray1, CSPSubarray2, CSPSubarray3, CBFSubarray1, CBFSubarray2, CBFSubarray3
):
    """Wait for Tango Deviceproxies to change states.

    :param CBF : tango.DeviceProxy CBF Controller DeviceProxy
    :param CSP : tango.DeviceProxy CSP Controller DeviceProxy
    :param CSPSubarray1 : tango.DeviceProxy Subarray DeviceProxy
    :param CSPSubarray2 : tango.DeviceProxy Subarray DeviceProxy
    :param CSPSubarray3 : tango.DeviceProxy Subarray DeviceProxy
    :param CBFSubarray1 : tango.DeviceProxy Subarray DeviceProxy
    :param CBFSubarray2 : tango.DeviceProxy Subarray DeviceProxy
    :param CBFSubarray3 : tango.DeviceProxy Subarray DeviceProxy
    """
    READY = False
    timer = 0
    while not READY:
        time.sleep(1)
        timer += 1
        if timer == 30:
            break
        device_proxies = [
            CSP,
            CBF,
            CBFSubarray1,
            CBFSubarray2,
            CBFSubarray3,
            CSPSubarray1,
            CSPSubarray2,
            CSPSubarray3,
        ]

        for dp in device_proxies:
            state = dp.State()
            server = dp.name()
            adminmode = dp.adminmode
            if state != DevState.OFF:
                logger.info(f"Still waiting for {server} to change state from {state} to OFF while Adminmode is {adminmode}")
                READY = False
                break
            else:
                READY = True
                logger.info(f"Device {server} is now in {state} state, adminmode {adminmode}")
    return


def main() -> None:  # noqa C901
    """Call the CBF On command."""
    logger.debug(f"Path of hw_config.yaml is {src_pth}")
    logger.debug(f"Destination Path of hw_config.yaml is {dest_pth}")

    CBF = DeviceProxy("mid_csp_cbf/sub_elt/controller")
    CSP = DeviceProxy("mid-csp/control/0")
    CSPSubarray1 = DeviceProxy("mid-csp/subarray/01")
    CSPSubarray2 = DeviceProxy("mid-csp/subarray/02")
    CSPSubarray3 = DeviceProxy("mid-csp/subarray/03")
    CBFSubarray1 = DeviceProxy("mid_csp_cbf/sub_elt/subarray_01")
    CBFSubarray2 = DeviceProxy("mid_csp_cbf/sub_elt/subarray_02")
    CBFSubarray3 = DeviceProxy("mid_csp_cbf/sub_elt/subarray_03")

    # Exit if CSP is already ON
    if CSP.State() == DevState.ON and CSP.adminmode == 0:
        logger.info("CSP is already ON")
        return

    if CSP.adminmode != 0:
        logger.info("Setting CSP adminmode to ONLINE")
        CSP.adminmode = 0
        wait_for_devices(
            CBF,
            CSP,
            CSPSubarray1,
            CSPSubarray2,
            CSPSubarray3,
            CBFSubarray1,
            CBFSubarray2,
            CBFSubarray3,
        )

    dish_config = {
        "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
        "dish_parameters": {
            "SKA001": {"vcc": 1, "k": 11},
            "SKA036": {"vcc": 2, "k": 101},
            "SKA063": {"vcc": 3, "k": 1127},
            "SKA100": {"vcc": 4, "k": 620},
        },
    }

    CSP.loaddishcfg(json.dumps(dish_config))

    # Next set simulation to false - hardware use!
    CBF.simulationMode = False
    cbf_sim_mode = CBF.simulationMode
    while cbf_sim_mode != 0:
        logger.info("Waiting for CBF to change simulationMode to False")
        time.sleep(1)
        cbf_sim_mode = CBF.simulationMode
    logger.info("CBF simulationMode is now False")

    # Timeout for long-running command
    CSP.commandTimeout = TIMEOUT
    logger.debug(f"commandTimeout simply set to {TIMEOUT * 1000}")

    CSP.set_timeout_millis(TIMEOUT * 1000)
    logger.debug(f"Sent set_timeout_millis({TIMEOUT * 1000}) command")

    logger.info("Turning CSP ON - this may take a while...")
    CSP.on([])
    k = 1
    # CBF.ping()
    while CBF.State() != DevState.ON:
        if k == 11:
            logger.error("Could not turn the CBF Controller on. Exiting.")
            sys.exit(1)

        def fib(n: int) -> int:
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
