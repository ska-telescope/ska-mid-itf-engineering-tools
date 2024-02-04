"""This script turns on the TalonDx using CSP On command."""
import sys
import time

from tango import DeviceProxy, DevState

TIMEOUT = 60


def main():
    """Call the CSP On command."""
    CSP = DeviceProxy("mid-csp/control/0")
    if CSP.adminmode != 0:
        print("Setting CSP adminmode to ONLINE")
        CSP.adminmode = 0
        while CSP.adminmode != 0:
            time.sleep(1)
    print(f"CSP adminmode is now {CSP.adminmode}")
    print(CSP.State())
    if CSP.State() == DevState.ON and CSP.adminmode == 0:
        print("CSP is already ON")
        sys.exit(0)
    while CSP.State() != DevState.OFF:
        print(f"Waiting for CSP to change state from {CSP.State()} to OFF")
        time.sleep(1)
        if CSP.State() == DevState.FAULT:
            print("CSP is in FAULT state. Exiting.")
            sys.exit(1)

    CSP.cbfSimulationMode = False
    CSP.commandTimeout = TIMEOUT
    CSP.on([])
    while CSP.State() != DevState.ON:
        time.sleep(1)
    print("CSP is ON")
    return


if __name__ == "__main__":
    main()
