# ska-mid-itf-engineering-tools

[![Documentation Status](https://readthedocs.org/projects/ska-mid-itf-engineering-tools/badge/?version=latest)](https://developer.skatelescope.org/projects/ska-mid-itf-engineering-tools/en/latest/?badge=latest)

## How to Use

Clone this repo:

```
git clone https://gitlab.com/ska-telescope/ska-mid-itf-engineering-tools.git
cd ska-mid-itf-engineering-tools
git submodule update --init --recursive
```


## Installation

### Using poetry

```
$ poetry install
...
$ poetry lock
...
$ poetry shell
...
$ ./setup.py install

$ ./src/ska_mid_itf_engineering_tools/tango_control/tangoctl -h
```

### Local install

```
$ sudo python ./setup.py install

$ ./src/ska_mid_itf_engineering_tools/tango_control/tangoctl -h
```

## Testing

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

## Dependency Checker

The dependency checker is a tool which looks at a project's dependencies and reports any stale dependencies to a Slack channel. It checks both Poetry dependencies and dependencies present in Helm charts.

### Configuration

The only configuration needed is to set the environment variable `DEPENDENCY_CHECKER_WEBHOOK_URL`. This is typically set as a masked Gitlab variable.

### Execution

The dependency checker Gitlab job, *check-dependencies*, is run as part of a scheduled pipeline on a weekly basis. It can also be executed manually from any pipeline. For this project, it reports stale dependencies to the [#atlas-dependencies](https://skao.slack.com/archives/C06MR162K24) channel.

## Tango control utility

### Getting help

To obtain help:

```$ tangoctl --help
Display version number
        tangoctl --version
Display help
        tangoctl --help
        tangoctl -h
Display Kubernetes namespaces
        tangoctl --show-ns
        tangoctl -n
Display Tango database address
        tangoctl --show-db [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -t [-N <NAMESPACE>|-H <HOST>]
Display Tango device names
        tangoctl --show-dev [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -d [-N <NAMESPACE>|-H <HOST>]
Display all devices
        tangoctl --full|--long|--quick|--short [--dry-run] [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -f|-l|-q|-s [-N <NAMESPACE>|-H <HOST>]
Filter on device name
        tangoctl --full|--long|--quick|--short -D <DEVICE> [-N <NAMESPACE>|-H <HOST>]
        tangoctl -f|-l|-q|-s --device=<DEVICE> [--namespace=<NAMESPACE>|--host=<HOST>]
Filter on attribute name
        tangoctl --full|--long|--quick|--short --attribute=<ATTRIBUTE> [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -f|-l|-q|-s -A <ATTRIBUTE> [-N <NAMESPACE>|-H <HOST>]
Filter on command name
        tangoctl --full|--long|--quick|--short --command=<COMMAND> [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -f|-l|-q|-s -C <COMMAND> [-N <NAMESPACE>|-H <HOST>]
Filter on property name
        tangoctl --full|--long|--quick|--short --property=<PROPERTY> [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -f|-l|-q|-s -P <PROPERTY> [-N <NAMESPACE>|--host=<HOST>]
Display known acronyms
        tangoctl -j
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

### Read all namespaces in Kubernetes cluster

The user must be logged into the Mid ITF VPN, otherwise this will time out.

```$ tangoctl --show-ns
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

### Read Tango devices

#### Read all Tango devices

This will display the name, current state and admin mode setting for each Tango device 
in the database. Note that output has been shorteneded. By default, device names starting 
with **dserver** or **sys** are not listed.

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 --list
DEVICE NAME                              STATE      ADMIN MODE  VERSION  CLASS
mid-csp/capability-fsp/0                 ON         ONLINE      2        MidCspCapabilityFsp
mid-csp/capability-vcc/0                 ON         ONLINE      2        MidCspCapabilityVcc
mid-csp/control/0                        DISABLE    OFFLINE     2        MidCspController
mid-csp/subarray/01                      DISABLE    OFFLINE     2        MidCspSubarray
mid-csp/subarray/02                      DISABLE    OFFLINE     2        MidCspSubarray
mid-csp/subarray/03                      DISABLE    OFFLINE     2        MidCspSubarray
mid-eda/cm/01                            ON         N/A         N/A      HdbConfigurationManager
mid-eda/es/01                            ON         N/A         N/A      HdbEventSubscriber
mid-sdp/control/0                        N/A        N/A         N/A      N/A
mid-sdp/queueconnector/01                N/A        N/A         N/A      N/A
mid-sdp/queueconnector/02                N/A        N/A         N/A      N/A
mid-sdp/queueconnector/03                N/A        N/A         N/A      N/A
mid-sdp/subarray/01                      N/A        N/A         N/A      N/A
mid-sdp/subarray/02                      N/A        N/A         N/A      N/A
mid-sdp/subarray/03                      N/A        N/A         N/A      N/A
mid_csp_cbf/fs_links/000                 DISABLE    OFFLINE     0.11.4   SlimLink
...
mid_csp_cbf/fs_links/015                 DISABLE    OFFLINE     0.11.4   SlimLink
mid_csp_cbf/fsp/01                       DISABLE    OFFLINE     0.11.4   Fsp
mid_csp_cbf/fsp/02                       DISABLE    OFFLINE     0.11.4   Fsp
mid_csp_cbf/fsp/03                       DISABLE    OFFLINE     0.11.4   Fsp
mid_csp_cbf/fsp/04                       DISABLE    OFFLINE     0.11.4   Fsp
mid_csp_cbf/fspCorrSubarray/01_01        DISABLE    OFFLINE     0.11.4   FspCorrSubarray
...
mid_csp_cbf/fspCorrSubarray/04_03        DISABLE    OFFLINE     0.11.4   FspCorrSubarray
mid_csp_cbf/fspPssSubarray/01_01         DISABLE    OFFLINE     0.11.4   FspPssSubarray
...
mid_csp_cbf/fspPssSubarray/04_03         DISABLE    OFFLINE     0.11.4   FspPssSubarray
mid_csp_cbf/fspPstSubarray/01_01         DISABLE    OFFLINE     0.11.4   FspPstSubarray
...
mid_csp_cbf/fspPstSubarray/04_03         DISABLE    OFFLINE     0.11.4   FspPstSubarray
mid_csp_cbf/power_switch/001             DISABLE    OFFLINE     0.11.4   PowerSwitch
mid_csp_cbf/power_switch/002             DISABLE    OFFLINE     0.11.4   PowerSwitch
mid_csp_cbf/power_switch/003             DISABLE    OFFLINE     0.11.4   PowerSwitch
mid_csp_cbf/slim/slim-fs                 DISABLE    OFFLINE     0.11.4   Slim
mid_csp_cbf/slim/slim-vis                DISABLE    OFFLINE     0.11.4   Slim
mid_csp_cbf/sub_elt/controller           DISABLE    OFFLINE     0.11.4   CbfController
mid_csp_cbf/sub_elt/subarray_01          DISABLE    OFFLINE     0.11.4   CbfSubarray
mid_csp_cbf/sub_elt/subarray_02          DISABLE    OFFLINE     0.11.4   CbfSubarray
mid_csp_cbf/sub_elt/subarray_03          DISABLE    OFFLINE     0.11.4   CbfSubarray
mid_csp_cbf/talon_board/001              DISABLE    OFFLINE     0.11.4   TalonBoard
...
mid_csp_cbf/talon_board/008              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_lru/001                DISABLE    OFFLINE     0.11.4   TalonLRU
...
mid_csp_cbf/talon_lru/004                DISABLE    OFFLINE     0.11.4   TalonLRU
mid_csp_cbf/talondx_log_consumer/001     DISABLE    OFFLINE     0.11.4   TalonDxLogConsumer
mid_csp_cbf/vcc/001                      DISABLE    OFFLINE     0.11.4   Vcc
...
mid_csp_cbf/vcc/008                      DISABLE    OFFLINE     0.11.4   Vcc
mid_csp_cbf/vcc_sw1/001                  DISABLE    OFFLINE     0.11.4   VccSearchWindow
...
mid_csp_cbf/vcc_sw2/008                  DISABLE    OFFLINE     0.11.4   VccSearchWindow
mid_csp_cbf/vis_links/000                DISABLE    OFFLINE     0.11.4   SlimLink
mid_csp_cbf/vis_links/001                DISABLE    OFFLINE     0.11.4   SlimLink
mid_csp_cbf/vis_links/002                DISABLE    OFFLINE     0.11.4   SlimLink
mid_csp_cbf/vis_links/003                DISABLE    OFFLINE     0.11.4   SlimLink
ska_mid/tm_central/central_node          ON         OFFLINE     0.12.2   CentralNodeMid
ska_mid/tm_leaf_node/csp_master          ON         OFFLINE     0.10.3   CspMasterLeafNode
ska_mid/tm_leaf_node/csp_subarray01      ON         OFFLINE     0.10.3   CspSubarrayLeafNodeMid
ska_mid/tm_leaf_node/csp_subarray_01     INIT       OFFLINE     0.11.4   TmCspSubarrayLeafNodeTest
ska_mid/tm_leaf_node/csp_subarray_02     INIT       OFFLINE     0.11.4   TmCspSubarrayLeafNodeTest
ska_mid/tm_leaf_node/d0001               ON         OFFLINE     0.8.1    DishLeafNode
...
ska_mid/tm_leaf_node/d0100               ON         OFFLINE     0.8.1    DishLeafNode
ska_mid/tm_leaf_node/sdp_master          ON         OFFLINE     0.14.2   SdpMasterLeafNode
ska_mid/tm_leaf_node/sdp_subarray01      ON         OFFLINE     0.14.2   SdpSubarrayLeafNode
ska_mid/tm_subarray_node/1               ON         OFFLINE     0.13.19  SubarrayNodeMid
```

### Filter by device name

To find all devices with **talon** in the name:

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D talon -l
DEVICE NAME                              STATE      ADMIN MODE  VERSION  CLASS
mid_csp_cbf/talon_board/001              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/002              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/003              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/004              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/005              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/006              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/007              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_board/008              DISABLE    OFFLINE     0.11.4   TalonBoard
mid_csp_cbf/talon_lru/001                DISABLE    OFFLINE     0.11.4   TalonLRU
mid_csp_cbf/talon_lru/002                DISABLE    OFFLINE     0.11.4   TalonLRU
mid_csp_cbf/talon_lru/003                DISABLE    OFFLINE     0.11.4   TalonLRU
mid_csp_cbf/talon_lru/004                DISABLE    OFFLINE     0.11.4   TalonLRU
mid_csp_cbf/talondx_log_consumer/001     DISABLE    OFFLINE     0.11.4   TalonDxLogConsumer
```

### Find attributes, commands or properties

It is possible to search for attributes, commands or properties by part of the name. This is not case sensitive.

#### Find attributes

To find all devices with attributes that contain **timeout**:

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -A timeout
DEVICE                                           ATTRIBUTE                                VALUE
mid-csp/control/0                                commandTimeout                           5
                                                 offCmdTimeoutExpired                     False
                                                 onCmdTimeoutExpired                      False
                                                 standbyCmdTimeoutExpired                 False
mid-csp/subarray/01                              commandTimeout                           5
                                                 timeoutExpiredFlag                       False
mid-csp/subarray/02                              commandTimeout                           5
                                                 timeoutExpiredFlag                       False
mid-csp/subarray/03                              commandTimeout                           5
                                                 timeoutExpiredFlag                       False
mid_csp_cbf/sub_elt/subarray_01                  assignResourcesTimeoutExpiredFlag        False
                                                 configureScanTimeoutExpiredFlag          False
                                                 releaseResourcesTimeoutExpiredFlag       False
mid_csp_cbf/sub_elt/subarray_02                  assignResourcesTimeoutExpiredFlag        False
                                                 configureScanTimeoutExpiredFlag          False
                                                 releaseResourcesTimeoutExpiredFlag       False
mid_csp_cbf/sub_elt/subarray_03                  assignResourcesTimeoutExpiredFlag        False
                                                 configureScanTimeoutExpiredFlag          False
                                                 releaseResourcesTimeoutExpiredFlag       False
```

To find all devices with attributes that contain **timeout**, without displaying values:

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -A timeout --dry-run
DEVICE                                           ATTRIBUTE
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

#### Find commands

To find all devices with commands that have **Telescope** in the name:

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -C Telescope
ska_mid/tm_central/central_node                  TelescopeOff
                                                 TelescopeOn
                                                 TelescopeStandby
```

To find all devices with commands that have **Outlet** in the name:

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -C Outlet
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

#### Find properties

To find all devices with properties that have **Power** in the name:

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -P Power
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

### Information on device

#### Full description of device

This display all information about a device. The input and output of commands are displayed where available.

```$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -f
Device            : mid_csp_cbf/talon_lru/001
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Description       : A Tango device
Acronyms          : Correlator Beam Former (CBF), Central Signal Processor (CSP), Line Replaceable Unit (LRU)
Database used     : True
Server host       : ds-talonlru-talonlru-001-0
Server ID         : TalonLRU/talonlru-001
Device class      : TalonLRU
Commands          : DebugDevice                    N/A
                                                   Not polled 
                                                   OUT The TCP port the debugger is listening on.
                    GetVersionInfo                 TalonLRU, ska_tango_base, 0.11.4, A set of generic base devices for SKA Telescope.
                                                   Not polled 
                                                   OUT Version strings
                    Init                           N/A
                                                   Not polled 
                    Off                            N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    On                             N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    Reset                          N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    Standby                        N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    State                          DISABLE
                                                   Polled     
                                                   OUT Device state
                    Status                         The device is in DISABLE state.
                                                   Not polled 
                                                   OUT Device status
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
                    loggingTargets                 tango::logger
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

#### Short display

This displays only status, commands, attributes and properties:

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -s
Device            : mid_csp_cbf/talon_lru/001
Admin mode        : 1
Commands          : DebugDevice                    N/A
                    GetVersionInfo                 TalonLRU, ska_tango_base, 0.11.4, A set of generic base devices for SKA Telescope.
                    Init                           N/A
                    Off                            N/A
                    On                             N/A
                    Reset                          N/A
                    Standby                        N/A
                    State                          DISABLE
                    Status                         The device is in DISABLE state.
Attributes        : PDU1PowerMode                  '0'
                    PDU2PowerMode                  '0'
                    State                          'DISABLE'
                    Status                         'The device is in DISABLE state.'
                    adminMode                      '1'
                    buildState                     'ska_tango_base, 0.11.4, A set of generic base devices for SKA Telescope.'
                    controlMode                    '0'
                    healthState                    '0'
                    loggingLevel                   '4'
                    loggingTargets                 tango::logger
                    simulationMode                 '1'
                    testMode                       '0'
                    versionId                      '0.11.4'
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

Display names only, without reading values:

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -s --dry-run
Device            : mid_csp_cbf/talon_lru/001
Admin mode        : 1
Commands          : DebugDevice
                    GetVersionInfo
                    Init
                    Off
                    On
                    Reset
                    Standby
                    State
                    Status
Attributes        : PDU1PowerMode
                    PDU2PowerMode
                    State
                    Status
                    adminMode
                    buildState
                    controlMode
                    healthState
                    loggingLevel
                    loggingTargets
                    simulationMode
                    testMode
                    versionId
Properties        : PDU1                          
                    PDU1PowerOutlet               
                    PDU2                          
                    PDU2PowerOutlet               
                    PDUCommandTimeout             
                    TalonDxBoard1                 
                    TalonDxBoard2                 
                    polled_attr
```

#### Quick/query mode

This displays a shortened form, with query sub-devices where available:

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -q
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

#### Error output

When a device attribute can not be read, a shortened error message is displayed:

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f
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

#### Dry run

To skip reading attribute values, use this option:

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f
Device            : mid_csp_cbf/talon_board/001
Admin mode        : 1
State             : DISABLE
Status            : The device is in DISABLE state.
Description       : A Tango device
Acronyms          : Correlator Beam Former (CBF), Central Signal Processor (CSP)
Database used     : True
Server host       : ds-talonboard-talon-001-0
Server ID         : TalonBoard/talon-001
Device class      : TalonBoard
Commands          : DebugDevice                    N/A
                                                   Not polled 
                                                   OUT The TCP port the debugger is listening on.
                    GetVersionInfo                 TalonBoard, ska_tango_base, 0.11.4, A set of generic base devices for SKA Telescope.
                                                   Not polled 
                                                   OUT Version strings
                    Init                           N/A
                                                   Not polled 
                    Off                            N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    On                             N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    Reset                          N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    Standby                        N/A
                                                   Not polled 
                                                   OUT (ReturnType, 'informational message')
                    State                          DISABLE
                                                   Polled     
                                                   OUT Device state
                    Status                         The device is in DISABLE state.
                                                   Not polled 
                                                   OUT Device status
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
                    FansPwmEnable                  <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    FpgaDieTemperature             <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    HumiditySensorTemperature      <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboRxLOLStatus                 <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboRxLOSStatus                 <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboRxVccVoltages               <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboTxFaultStatus               <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboTxLOLStatus                 <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboTxLOSStatus                 <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboTxTemperatures              <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    MboTxVccVoltages               <ERROR> AttributeError: 'TalonBoardComponentManager' object has no attribute '_hostname'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
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
                    comms_iopll_locked_fault       <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    controlMode                    '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    e100g_0_pll_fault              <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    e100g_1_pll_fault              <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    emif_bl_fault                  <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    emif_br_fault                  <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    emif_tr_fault                  <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    fs_iopll_locked_fault          <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    healthState                    '0'
                                                   Polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    iopll_locked_fault             <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    loggingLevel                   '4'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    loggingTargets                 tango::logger
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    simulationMode                 '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    slim_pll_fault                 <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    system_clk_fault               <ERROR> Talon Status Device is not available
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : <N/A>
                    testMode                       '0'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
                    versionId                      '0.11.4'
                                                   Not polled
                                                   Event change : Not specified
                                                   Quality : ATTR_VALID
Properties        : HpsMasterServer                dshpsmaster
                    InfluxDbAuthToken              ikIDRLicRaMxviUJRqyE8bKF1Y_sZnaHc9MkWZY92jxg1isNPIGCyLtaC8EjbOhsT_kTzjt12qenB4g7-UOrog==
                    InfluxDbBucket                 talon
                    InfluxDbOrg                    ska
                    InfluxDbPort                   8086
                    Instance                       talon1_test
                    TalonDx100GEthernetServer      ska-talondx-100-gigabit-ethernet-ds
                    TalonDxBoardAddress            192.168.8.1
                    TalonDxSysIdServer             ska-talondx-sysid-ds
                    TalonStatusServer              ska-talondx-status-ds
                    polled_attr                    state  1000
                                                   healthstate  3000
                                                   adminmode  3000
```

## Examples

```
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 --show-dev
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D talon -l
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -A timeout
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -C Telescope
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -P Power
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -f
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -s
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -q
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --dry
```
