"""This script turns on the TalonDx using CSP On command."""

# import os
import json
import logging
import sys
import time
import os
import subprocess

from ska_ser_logging import configure_logging
from tango import DeviceProxy, DevState

TIMEOUT = 60


def main():  # noqa C901
    """Call the CBF On command."""
    configure_logging(logging.DEBUG)
    logger = logging.getLogger(__name__)

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
        READY = False
        timer = 0
        while not READY:
            time.sleep(1)
            timer += 1
            if timer == 30:
                break
            if CSPSubarray1.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CSP Subarray1 to change state from {CSPSubarray1.State()} to OFF"
                )
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CSPSubarray2.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CSP Subarray2 to change state from {CSPSubarray2.State()} to OFF"
                )
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CSPSubarray3.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CSP Subarray3 to change state from {CSPSubarray3.State()} to OFF"
                )
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CBFSubarray1.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CBF Subarray1 to change state from {CBFSubarray1.State()} to OFF"
                )
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CBFSubarray2.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CBF Subarray2 to change state from {CBFSubarray2.State()} to OFF"
                )
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CBFSubarray3.State() != DevState.OFF:
                logger.info(
                    f"Waiting for CBF Subarray3 to change state from {CBFSubarray3.State()} to OFF"
                )
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CBF.State() != DevState.OFF:
                logger.info(f"Waiting for CBF to change state from {CBF.State()} to OFF")
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
            if CSP.State() != DevState.OFF:
                logger.info(f"Waiting for CSP to change state from {CSP.State()} to OFF")
                READY = False
                logger.debug("Exiting loop - device not ready")
                continue
            else:
                READY = True
        logger.info(f"CSP adminmode is now {CSP.adminmode}")
        logger.info(f"CSP State is now {CSP.State()}")
        logger.info(f"CBF adminmode is now {CBF.adminmode}")
        logger.info(f"CBF State is now {CBF.State()}")
        logger.info(f"CSP Subarray1 State is now {CSPSubarray1.State()}")
        logger.info(f"CSP Subarray2 State is now {CSPSubarray2.State()}")
        logger.info(f"CSP Subarray3 State is now {CSPSubarray3.State()}")
        logger.info(f"CBF Subarray1 State is now {CBFSubarray1.State()}")
        logger.info(f"CBF Subarray2 State is now {CBFSubarray2.State()}")
        logger.info(f"CBF Subarray3 State is now {CBFSubarray3.State()}")

    ns = os.environ["KUBE_NAMESPACE"]
    pth = os.environ["MCS_CONFIG_FILE_PATH"]
    subprocess.run(
        f"kubectl cp {pth}/hw_config.yaml {ns}/ds-cbfcontroller-controller-0:/app/mnt/hw_config/hw_config.yaml"
    )

    CBF.Init()

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
    while CBF.simulationMode != 0:
        logger.info(f"Waiting for CBF to change simulationMode from {CBF.simulationMode} to False")
        time.sleep(1)
    logger.info(f"CBF simulationMode is now {CBF.simulationMode}")

    # Timeout for long-running command
    CSP.commandTimeout = TIMEOUT
    logger.debug(f"commandTimeout simply set to {TIMEOUT}")

    logger.info("Turning CSP ON - this may take a while...")
    CSP.on([])
    k = 1
    while CBF.State() != DevState.ON:
        if k == 10:
            sys.exit(1)

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
