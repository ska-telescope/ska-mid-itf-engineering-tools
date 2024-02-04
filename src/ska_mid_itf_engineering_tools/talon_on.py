"""This script turns on the TalonDx using CSP On command."""
import sys
import time

from tango import DeviceProxy, DevState

TIMEOUT = 60


def main():
    """Call the CSP On command."""
    CSP = DeviceProxy("mid-csp/control/0")
    CSP.adminmode = 0
    print(CSP.adminmode)
    print(CSP.State())
    if CSP.State() == DevState.ON and CSP.adminmode == 0:
        print("CSP is already ON")
        sys.exit(0)
    if CSP.adminmode != 0:
        print("CSP admin mode not set to ONLINE")
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
