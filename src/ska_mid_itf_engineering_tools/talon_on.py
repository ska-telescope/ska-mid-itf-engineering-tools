"""This script turns on the TalonDx using CSP On command."""

import sys
import time

from tango import DeviceProxy, DevState

TIMEOUT = 60


def main():
    """Call the CBF On command."""
    CBF = DeviceProxy(
        "mid_csp_cbf/sub_elt/controller"
    )  # This is a direct call on the CBF MCS, not via the CSP.
    CSP = DeviceProxy("mid-csp/control/0")
    CSPSubarray = DeviceProxy("mid-csp/subarray/01")
    CBFSubarray = DeviceProxy("mid_csp_cbf/sub_elt/subarray_01")

    # Exit if CSP is already ON
    if CSP.State() == DevState.ON and CSP.adminmode == 0:
        print("CSP is already ON")
        return

    print(f"CSP Admin mode is now {CSP.adminmode}")
    if CSP.adminmode != 0:
        print("Setting CSP adminmode to ONLINE")
        CSP.adminmode = 0
        while (
            CSP.adminmode != 0
            or CSPSubarray.State() != DevState.OFF
            or CBFSubarray.State() != DevState.OFF
        ):
            print(f"Waiting for CSP to change adminmode from {CSP.adminmode} to ONLINE")
            print(f"Waiting for CSP Subarray to change state from {CSPSubarray.State()} to OFF")
            print(f"Waiting for CBF Subarray to change state from {CBFSubarray.State()} to OFF")
            time.sleep(1)
        print(f"CSP adminmode is now {CSP.adminmode}")
        print(f"CSP State is now {CSP.State()}")
        print(f"CSP Subarray State is now {CSPSubarray.State()}")
        print(f"CBF Subarray State is now {CBFSubarray.State()}")

    if CSP.State() == DevState.FAULT:
        print("CSP is in FAULT state. Exiting.")
        sys.exit(1)

    # Next set simulation to false - hardware use!
    CBF.simulationMode = False
    print(f"CBF simulationMode is now {CBF.simulationMode}")

    # Timeout for long-running command
    CSP.commandTimeout = TIMEOUT
    print("Turning CSP ON - this may take a while...")
    CSP.on([])
    while CSP.State() != DevState.ON:
        print(f"Waiting for CSP to change state from {CSP.State()} to ON")
        time.sleep(1)
    print("CSP is ON")
    return


# def csp_on_script():
#     """Call the CSP On command."""
#     print(f"CSP Admin mode is now {CSP.adminmode}")
#     if CSP.adminmode != 0:
#         print("Setting CSP adminmode to ONLINE")
#         CSP.adminmode = 0
#         while CSP.adminmode != 0:
#             time.sleep(1)
#     print(f"CSP adminmode is now {CSP.adminmode}")
#     print(f"CSP State is now {CSP.State()}")
#     if CSP.State() == DevState.ON and CSP.adminmode == 0:
#         print("CSP is already ON")
#         sys.exit(0)
#     while CSP.State() != DevState.OFF:
#         print(f"Waiting for CSP to change state from {CSP.State()} to OFF")
#         time.sleep(1)
#         if CSP.State() == DevState.FAULT:
#             print("CSP is in FAULT state. Exiting.")
#             sys.exit(1)

#     CSP.cbfSimulationMode = False
#     print(f"CSP cbfSimulationMode is now {CSP.cbfSimulationMode}")
#     CSP.commandTimeout = TIMEOUT
#     print("Turning CSP ON - this may take a while...")
#     CSP.on([])
#     while CSP.State() != DevState.ON:
#         print(f"Waiting for CSP to change state from {CSP.State()} to ON")
#         time.sleep(1)
#     print("CSP is ON")
#     return


if __name__ == "__main__":
    print("Executing latest version")
    main()
