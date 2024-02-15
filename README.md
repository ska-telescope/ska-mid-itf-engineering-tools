# ska-mid-itf-engineering-tools

[![Documentation Status](https://readthedocs.org/projects/ska-mid-itf-engineering-tools/badge/?version=latest)](https://developer.skatelescope.org/projects/ska-mid-itf-engineering-tools/en/latest/?badge=latest)

## How to Use

Clone this repo: 
```
git clone https://gitlab.com/ska-telescope/ska-mid-itf-engineering-tools.git
cd ska-mid-itf-engineering-tools
git submodule update --init --recursive
```

Build a new Docker image for the project:
```
$ make oci-build
[...]
[+] Building 111.7s (14/14) FINISHED 
[...]
```

Install python requirements:
```
poetry install
```

Run python-test:
```
$ poetry shell
$ make python-test

pytest 6.2.5
PYTHONPATH=/home/ubuntu/ska-mid-itf-engineering-tools/src:/app/src:  pytest  \
 --cov=src --cov-report=term-missing --cov-report html:build/reports/code-coverage --cov-report xml:build/reports/code-coverage.xml --junitxml=build/reports/unit-tests.xml tests/
=============================================================================================== test session starts ================================================================================================
platform linux -- Python 3.10.12, pytest-6.2.5, py-1.11.0, pluggy-1.3.0
rootdir: /home/ubuntu/ska-mid-itf-engineering-tools, configfile: pyproject.toml
plugins: cov-4.1.0, metadata-2.0.4, bdd-5.0.0, json-report-1.5.0, repeat-0.9.3, ska-ser-skallop-2.29.6
collected 4 items                                                                                                                                                                                                  

tests/functional/tmc/test_deployment.py ....                                                                                                                                                                 [100%]

----------------------------------------------------------- generated xml file: /home/ubuntu/ska-mid-itf-engineering-tools/build/reports/unit-tests.xml ------------------------------------------------------------

---------- coverage: platform linux, python 3.10.12-final-0 ----------
Name                                                Stmts   Miss  Cover   Missing
---------------------------------------------------------------------------------
src/ska_mid_itf_engineering_tools/__init__.py           0      0   100%
src/ska_mid_itf_engineering_tools/tmc_dish_ids.py      47     12    74%   74, 167, 169, 171, 173, 199-205, 209-214
---------------------------------------------------------------------------------
TOTAL                                                  47     12    74%
Coverage HTML written to dir build/reports/code-coverage
Coverage XML written to file build/reports/code-coverage.xml

================================================================================================ 4 passed in 0.10s =================================================================================================

```

Python linting:
```
$ make python-lint
[...]
--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

# Tango information utility

## Getting help

To obtain help:

```
$ tango_info.py --help
Display version number
        tango_info.py --version
Display help
        tango_info.py --help
        tango_info.py -h
Display Kubernetes namespaces
        tango_info.py --show-ns
        tango_info.py -n
Display Tango database address
        tango_info.py --show-db [--namespace=<NAMESPACE>|--host=<HOST>]
        tango_info.py -t [-N <NAMESPACE>|-H <HOST>]
Display Tango device names
        tango_info.py --show-dev [--namespace=<NAMESPACE>|--host=<HOST>]
        tango_info.py -d [-N <NAMESPACE>|-H <HOST>]
Display all devices
        tango_info.py --full|--long|--quick|--short [--dry-run] [--namespace=<NAMESPACE>|--host=<HOST>]
        tango_info.py -f|-l|-q|-s [-N <NAMESPACE>|-H <HOST>]
Filter on device name
        tango_info.py --full|--long|--quick|--short -D <DEVICE> [-N <NAMESPACE>|-H <HOST>]
        tango_info.py -f|-l|-q|-s --device=<DEVICE> [--namespace=<NAMESPACE>|--host=<HOST>]
Filter on attribute name
        tango_info.py --full|--long|--quick|--short --attribute=<ATTRIBUTE> [--namespace=<NAMESPACE>|--host=<HOST>]
        tango_info.py -f|-l|-q|-s -A <ATTRIBUTE> [-N <NAMESPACE>|-H <HOST>]
Filter on command name
        tango_info.py --full|--long|--quick|--short --command=<COMMAND> [--namespace=<NAMESPACE>|--host=<HOST>]
        tango_info.py -f|-l|-q|-s -C <COMMAND> [-N <NAMESPACE>|-H <HOST>]
Filter on property name
        tango_info.py --full|--long|--quick|--short --property=<PROPERTY> [--namespace=<NAMESPACE>|--host=<HOST>]
        tango_info.py -f|-l|-q|-s -P <PROPERTY> [-N <NAMESPACE>|--host=<HOST>]
Display known acronyms
        tango_info.py -j
where:
        -f                              display in full
        -l                              display device name and status on one line
        -q                              display device name, status and query devices
        -s                              display device name and status only
        -f                              get commands, attributes and properties regardless of state
        --device=<DEVICE>               device name, e.g. 'csp' (not case sensitive, only a part is needed)
        --namespace=<NAMESPACE>         Kubernetes namespace for Tango database, e.g. 'integration'
        --host=<HOST>                   Tango database host and port, e.g. 10.8.13.15:10000
        --attribute=<ATTRIBUTE>         attribute name, e.g. 'obsState' (case sensitive)
        --command=<COMMAND>             command name, e.g. 'Status' (case sensitive)
        -D <DEVICE>                     device name, e.g. 'csp' (not case sensitive, only a part is needed)
        -N <NAMESPACE>                  Kubernetes namespace for Tango database, default is ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2
        -H <HOST>                       Tango database host and port, e.g. 10.8.13.15:10000
        -A <ATTRIBUTE>                  attribute name, e.g. 'obsState' (case sensitive)
        -C <COMMAND>                    command name, e.g. 'Status' (case sensitive)
```

## Read all namespaces in Kubernetes cluster

The user must be logged into the Mid ITF VPN, otherwise this will time out.

```
$ tango_info.py --show-ns
Namespaces : 53
        advanced-tango-training
        advanced-tango-training-sdp
        binderhub
        calico-apiserver
        calico-operator
        calico-system
        ci-dish-lmc-ska001-at-1838-update-main
        ci-dish-lmc-ska036-at-1838-update-main
        ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2
        ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2-sdp
        ci-ska-mid-itf-at-1838-update-main
        ci-ska-mid-itf-at-1838-update-main-sdp
        ci-ska-mid-itf-sah-1486
        ci-ska-mid-itf-sah-1486-sdp
        default
        dish-lmc-ska001
        dish-lmc-ska036
        dish-lmc-ska063
        dish-lmc-ska100
        dish-structure-simulators
        dishlmc-integration-ska001
        ds-sim-ska001
        extdns
        file-browser
        gitlab
        infra
        ingress-nginx
        integration
        integration-sdp
        integration-ska-mid-dish-spfc
        itf-ska-dish-lmc-spf
        kube-node-lease
        kube-public
        kube-system
        kyverno
        metallb-system
        miditf-lmc-002-ds
        miditf-lmc-003-karoo-sims
        miditf-lmc-005-spfrx
        register-spfc
        rook-ceph
        secrets-store-csi-driver
        ska-db-oda
        ska-tango-archiver
        ska-tango-operator
        sonobuoy
        spookd
        tango-tar-pvc
        tango-util
        taranta
        test-equipment
        test-spfc
        vault
```

## Read Tango devices

### Read all Tango devices

This will display the name, current state and admin mode setting for each Tango device 
in the database. Note that output has been shorteneded. By default, device names starting with **dserver** or sys **are** not listed.

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 --show-dev
STATE      DEVICE NAME                              ADMIN MODE
ON         mid-csp/capability-fsp/0                 0
ON         mid-csp/capability-vcc/0                 0
DISABLE    mid-csp/control/0                        1
DISABLE    mid-csp/subarray/01                      1
DISABLE    mid-csp/subarray/02                      1
DISABLE    mid-csp/subarray/03                      1
ON         mid-eda/cm/01                            None
ON         mid-eda/es/01                            None
None       mid-sdp/control/0                        None
None       mid-sdp/queueconnector/01                None
None       mid-sdp/queueconnector/02                None
None       mid-sdp/queueconnector/03                None
None       mid-sdp/subarray/01                      None
None       mid-sdp/subarray/02                      None
None       mid-sdp/subarray/03                      None
DISABLE    mid_csp_cbf/fs_links/000                 1
...
DISABLE    mid_csp_cbf/fs_links/015                 1
DISABLE    mid_csp_cbf/fsp/01                       1
DISABLE    mid_csp_cbf/fsp/02                       1
DISABLE    mid_csp_cbf/fsp/03                       1
DISABLE    mid_csp_cbf/fsp/04                       1
DISABLE    mid_csp_cbf/fspCorrSubarray/01_01        1
...
DISABLE    mid_csp_cbf/fspCorrSubarray/04_03        1
DISABLE    mid_csp_cbf/fspPssSubarray/01_01         1
...
DISABLE    mid_csp_cbf/fspPssSubarray/04_03         1
DISABLE    mid_csp_cbf/fspPstSubarray/01_01         1
...
DISABLE    mid_csp_cbf/fspPstSubarray/04_03         1
DISABLE    mid_csp_cbf/power_switch/001             1
DISABLE    mid_csp_cbf/power_switch/002             1
DISABLE    mid_csp_cbf/power_switch/003             1
DISABLE    mid_csp_cbf/slim/slim-fs                 1
DISABLE    mid_csp_cbf/slim/slim-vis                1
DISABLE    mid_csp_cbf/sub_elt/controller           1
DISABLE    mid_csp_cbf/sub_elt/subarray_01          1
DISABLE    mid_csp_cbf/sub_elt/subarray_02          1
DISABLE    mid_csp_cbf/sub_elt/subarray_03          1
DISABLE    mid_csp_cbf/talon_board/001              1
...
DISABLE    mid_csp_cbf/talon_board/008              1
DISABLE    mid_csp_cbf/talon_lru/001                1
DISABLE    mid_csp_cbf/talon_lru/002                1
DISABLE    mid_csp_cbf/talon_lru/003                1
DISABLE    mid_csp_cbf/talon_lru/004                1
DISABLE    mid_csp_cbf/talondx_log_consumer/001     1
DISABLE    mid_csp_cbf/vcc/001                      1
...
DISABLE    mid_csp_cbf/vcc/008                      1
DISABLE    mid_csp_cbf/vcc_sw1/001                  1
...
DISABLE    mid_csp_cbf/vcc_sw1/008                  1
DISABLE    mid_csp_cbf/vcc_sw2/001                  1
...
DISABLE    mid_csp_cbf/vcc_sw2/008                  1
DISABLE    mid_csp_cbf/vis_links/000                1
DISABLE    mid_csp_cbf/vis_links/001                1
DISABLE    mid_csp_cbf/vis_links/002                1
DISABLE    mid_csp_cbf/vis_links/003                1
ON         ska_mid/tm_central/central_node          1
ON         ska_mid/tm_leaf_node/csp_master          1
ON         ska_mid/tm_leaf_node/csp_subarray01      1
INIT       ska_mid/tm_leaf_node/csp_subarray_01     1
INIT       ska_mid/tm_leaf_node/csp_subarray_02     1
ON         ska_mid/tm_leaf_node/d0001               1
ON         ska_mid/tm_leaf_node/d0036               1
ON         ska_mid/tm_leaf_node/d0063               1
ON         ska_mid/tm_leaf_node/d0100               1
ON         ska_mid/tm_leaf_node/sdp_master          1
ON         ska_mid/tm_leaf_node/sdp_subarray01      1
ON         ska_mid/tm_subarray_node/1               1
```

### Filter by device name

To find all devices with **talon** in the name:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D talon -d
STATE      DEVICE NAME                              ADMIN MODE
DISABLE    mid_csp_cbf/talon_board/001              1
DISABLE    mid_csp_cbf/talon_board/002              1
DISABLE    mid_csp_cbf/talon_board/003              1
DISABLE    mid_csp_cbf/talon_board/004              1
DISABLE    mid_csp_cbf/talon_board/005              1
DISABLE    mid_csp_cbf/talon_board/006              1
DISABLE    mid_csp_cbf/talon_board/007              1
DISABLE    mid_csp_cbf/talon_board/008              1
DISABLE    mid_csp_cbf/talon_lru/001                1
DISABLE    mid_csp_cbf/talon_lru/002                1
DISABLE    mid_csp_cbf/talon_lru/003                1
DISABLE    mid_csp_cbf/talon_lru/004                1
DISABLE    mid_csp_cbf/talondx_log_consumer/001     1
```

## Find attributes, commands or properties

It is possible to search for attributes, commands or properties by part of the name. This is not case sensitive.

### Find attributes

To find all devices with attributes that contain **timeout**:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -A timeout
mid-csp/control/0                                commandTimeout
                                                 offCmdTimeoutExpired
                                                 onCmdTimeoutExpired
                                                 standbyCmdTimeoutExpired
mid-csp/subarray/01                              commandTimeout
                                                 timeoutExpiredFlag
mid-csp/subarray/02                              commandTimeout
                                                 timeoutExpiredFlag
mid-csp/subarray/03                              commandTimeout
                                                 timeoutExpiredFlag
mid_csp_cbf/sub_elt/subarray_01                  assignResourcesTimeoutExpiredFlag
                                                 configureScanTimeoutExpiredFlag
                                                 releaseResourcesTimeoutExpiredFlag
mid_csp_cbf/sub_elt/subarray_02                  assignResourcesTimeoutExpiredFlag
                                                 configureScanTimeoutExpiredFlag
                                                 releaseResourcesTimeoutExpiredFlag
mid_csp_cbf/sub_elt/subarray_03                  assignResourcesTimeoutExpiredFlag
                                                 configureScanTimeoutExpiredFlag
                                                 releaseResourcesTimeoutExpiredFlag
```

### Find commands

To find all devices with commands that have **Telescope** in the name:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -C Telescope
ska_mid/tm_central/central_node                  TelescopeOff
                                                 TelescopeOn
                                                 TelescopeStandby`
To find all devices with commands that have **Outlet** in the name: 
`$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -C Outlet
mid_csp_cbf/power_switch/001                     GetOutletPowerMode
                                                 TurnOffOutlet
                                                 TurnOnOutlet
mid_csp_cbf/power_switch/002                     GetOutletPowerMode
                                                 TurnOffOutlet
                                                 TurnOnOutlet
mid_csp_cbf/power_switch/003                     GetOutletPowerMode
                                                 TurnOffOutlet
                                                 TurnOnOutlet
```

### Find properties

To find all devices with properties that have **Power** in the name:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -P Power
mid_csp_cbf/power_switch/001                     PowerSwitchIp
                                                 PowerSwitchLogin
                                                 PowerSwitchModel
                                                 PowerSwitchPassword
mid_csp_cbf/power_switch/002                     PowerSwitchIp
                                                 PowerSwitchLogin
                                                 PowerSwitchModel
                                                 PowerSwitchPassword
mid_csp_cbf/power_switch/003                     PowerSwitchIp
                                                 PowerSwitchLogin
                                                 PowerSwitchModel
                                                 PowerSwitchPassword
mid_csp_cbf/sub_elt/controller                   PowerSwitch
mid_csp_cbf/talon_lru/001                        PDU1PowerOutlet
                                                 PDU2PowerOutlet
mid_csp_cbf/talon_lru/002                        PDU1PowerOutlet
                                                 PDU2PowerOutlet
mid_csp_cbf/talon_lru/003                        PDU1PowerOutlet
                                                 PDU2PowerOutlet
mid_csp_cbf/talon_lru/004                        PDU1PowerOutlet
                                                 PDU2PowerOutlet
```

## Information on device

### Full description of device

This display all information about a device. The input and output of commands are displayed where available.

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -f
Device            : mid_csp_cbf/talon_lru/001
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Description       : A Tango device
Acronyms          : Correlator Beam Former (CBF), Central Signal Processor (CSP), Line Replaceable Unit (LRU)
Database used     : True
Device class      : TalonLRU
Server host       : ds-talonlru-talonlru-001-0
Server ID         : TalonLRU/talonlru-001
Commands            DebugDevice                    Not polled  OUT The TCP port the debugger is listening on.
                    GetVersionInfo                 Not polled  OUT Version strings
                    Init                           Not polled 
                    Off                            Not polled  OUT (ReturnType, 'informational message')
                    On                             Not polled  OUT (ReturnType, 'informational message')
                    Reset                          Not polled  OUT (ReturnType, 'informational message')
                    Standby                        Not polled  OUT (ReturnType, 'informational message')
                    State                          Polled      OUT Device state
                    Status                         Not polled  OUT Device status
Attributes        : PDU1PowerMode                  '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    PDU2PowerMode                  '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    State                          'DISABLE'
                                                   Polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    Status                         'The device is in DISABLE state.'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    adminMode                      '1'
                                                   Polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    buildState                     'ska_tango_base, 0.11.4, A set of generic base devices for SKA Telescope.'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    controlMode                    '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    healthState                    '0'
                                                   Polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    loggingLevel                   '4'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    loggingTargets                
                                                     tango::logger
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    simulationMode                 '1'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    testMode                       '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    versionId                      '0.11.4'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
Properties        : PDU1                           002
                    PDU1PowerOutlet                AA41
                    PDU2                           002
                    PDU2PowerOutlet                AA41
                    PDUCommandTimeout              20
                    TalonDxBoard1                  001
                    TalonDxBoard2                  002
                    polled_attr                    state  1000
                                                   healthstate  3000
                                                   adminmode  3000
```

### Short display

This displays only status, commands, attributes and properties:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -s
Device            : mid_csp_cbf/talon_lru/001
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Commands          : DebugDevice
                  : GetVersionInfo
                  : Init
                  : Off
                  : On
                  : Reset
                  : Standby
                  : State
                  : Status
Attributes        : PDU1PowerMode
                  : PDU2PowerMode
                  : State
                  : Status
                  : adminMode
                  : buildState
                  : controlMode
                  : healthState
                  : loggingLevel
                  : loggingTargets
                  : simulationMode
                  : testMode
                  : versionId
Properties        : PDU1
                  : PDU1PowerOutlet
                  : PDU2
                  : PDU2PowerOutlet
                  : PDUCommandTimeout
                  : polled_attr
                  : TalonDxBoard1
                  : TalonDxBoard2
```

### Quick/query mode

This displays a shortened form, with query sub-devices where available:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -q
Device            : mid_csp_cbf/talon_lru/001 9 commands, 13 attributes
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Description       : A Tango device
Acronyms          : Correlator Beam Former (CBF), Central Signal Processor (CSP), Line Replaceable Unit (LRU)
Device class      : TalonLRU
Server host       : ds-talonlru-talonlru-001-0
Server ID         : TalonLRU/talonlru-001
Logging target    : <N/A>
Query sub-devices : <N/A>
```

### Error output

When a device attribute can not be read, a shortened error message is displayed:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f
Tango host        : tango-databaseds.ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2.svc.miditf.internal.skao.int:10000

Device            : mid_csp_cbf/talon_board/001
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Description       : A Tango device
Acronyms          : Correlator Beam Former (CBF), Central Signal Processor (CSP)
Database used     : True
Device class      : TalonBoard
Server host       : ds-talonboard-talon-001-0
Server ID         : TalonBoard/talon-001
Commands            DebugDevice                    Not polled  OUT The TCP port the debugger is listening on.
                    GetVersionInfo                 Not polled  OUT Version strings
                    Init                           Not polled 
                    Off                            Not polled  OUT (ReturnType, 'informational message')
                    On                             Not polled  OUT (ReturnType, 'informational message')
                    Reset                          Not polled  OUT (ReturnType, 'informational message')
                    Standby                        Not polled  OUT (ReturnType, 'informational message')
                    State                          Polled      OUT Device state
                    Status                         Not polled  OUT Device status
Attributes        : BitstreamChecksum              <ERROR> System ID Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    BitstreamVersion               <ERROR> System ID Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    DIMMTemperatures               <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    FansFault                      <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    FansPwm                        <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
...
```

### Dry run

To skip reading attribute values, use this option:

```
$ tango_info.py --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --dry
Tango host        : tango-databaseds.ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2.svc.miditf.internal.skao.int:10000

Device            : mid_csp_cbf/talon_board/001
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Description       : A Tango device
Acronyms          : Correlator Beam Former (CBF), Central Signal Processor (CSP)
Database used     : True
Device class      : TalonBoard
Server host       : ds-talonboard-talon-001-0
Server ID         : TalonBoard/talon-001
Commands            DebugDevice                    Not polled  OUT The TCP port the debugger is listening on.
                    GetVersionInfo                 Not polled  OUT Version strings
                    Init                           Not polled 
                    Off                            Not polled  OUT (ReturnType, 'informational message')
                    On                             Not polled  OUT (ReturnType, 'informational message')
                    Reset                          Not polled  OUT (ReturnType, 'informational message')
                    Standby                        Not polled  OUT (ReturnType, 'informational message')
                    State                          Polled      OUT Device state
                    Status                         Not polled  OUT Device status
Attributes        : BitstreamChecksum              <N/A>
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    BitstreamVersion               <N/A>
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    DIMMTemperatures               <N/A>
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    FansFault                      <N/A>
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    FansPwm                        <N/A>
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
...
```
