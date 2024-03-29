# ska-mid-itf-engineering-tools

[![Documentation Status](https://readthedocs.org/projects/ska-mid-itf-engineering-tools/badge/?version=latest)](https://developer.skatelescope.org/projects/ska-mid-itf-engineering-tools/en/latest/?badge=latest)

## Introduction

This repo provides a suite of utilities for use in the Mid ITF environment:
* *tangoctl*, a utility to query and test Tanfo devices
* *tangoktl*, a utility to query and test Tanfo devices running in a Kubernetes cluster
* *dependency_checker*, a utility to check Helm and Poetry dependencies

## How to Use

Clone this repo:

```
$ git clone https://gitlab.com/ska-telescope/ska-mid-itf-engineering-tools.git
$ cd ska-mid-itf-engineering-tools
$ git submodule update --init --recursive
```

## Installation of *tangoctl*

### How to get and set Tango host

#### Using *kubectl*

Read the external IP address of the service _tango-databaseds_ in the Kubernetes namespace of interest, e.g. _integration_:

```
$ kubectl get service tango-databaseds --namespace integration
NAME               TYPE           CLUSTER-IP    EXTERNAL-IP     PORT(S)           AGE
tango-databaseds   LoadBalancer   10.110.24.5   10.164.10.161   10000:32207/TCP   6d7h
$ export TANGO_HOST=10.164.10.161:10000
```

#### Using *tangoktl*

If tangoktl is installed (see below) it can be used to get the tango host setting:

```
$ tangoktl.py -K integration -t
TANGO_HOST=tango-databaseds.integration.svc.miditf.internal.skao.int:10000
TANGO_HOST=10.164.10.161:10000
$ export TANGO_HOST=10.164.10.161:10000
```

### Using poetry

Activate poetry:

```
$ poetry install
$ poetry lock
$ poetry shell
$ source .venv/bin/activate
```

Inside the poetry shell, any of the following should work:

```
# tangoctl -h
# ./src/ska_mid_itf_engineering_tools/tango_control/tangoctl.py -h
```

To use *tangoktl* in Poetry, you will need to log in on infra:

```
# infra login https://boundary.skao.int --enable-ssh
# infra use za-itf-k8s-master01-k8s
# tangoctl -k
```

### Using Docker

Build a Docker image with your choice of Tango version (both of these have been tested to work):

```
$ docker build . -t tangoctl -f Dockerfile --build-arg OCI_IMAGE_VERSION="artefact.skao.int/ska-tango-images-pytango-builder:9.4.2"
$ docker build . -t tangoctl -f Dockerfile --build-arg OCI_IMAGE_VERSION="artefact.skao.int/ska-tango-images-pytango-builder:9.5.0"
```

Run the Docker image:

```
$ docker run --network host -it tangoctl /bin/bash
root@346b0ffcf616:/app# ./src/ska_mid_itf_engineering_tools/tango_control/tangoctl.py -h
```

To use *tangoktl* in Docker, you will need to log in on infra:

```
# infra login https://boundary.skao.int --enable-ssh
# infra use za-itf-k8s-master01-k8s
# tangoctl -k
```

### Local install

To run *tangoctl* or *tangoktl* on your own computer:

```
$ mkdir -p ${HOME}/bin
$ export PATH=${HOME}/bin:${PATH}
$ ln -s src/ska_mid_itf_engineering_tools/tango_control/tangoctl.py ${HOME}/bin/tangoctl
$ ln -s src/ska_mid_itf_engineering_tools/tango_kontrol/tangoktl.py ${HOME}/bin/tangoktl
```

Also update the Python path and check:

```
$ export PYTHONPATH=${PYTHONPATH}:{PWD}/src/ska_mid_itf_engineering_tools
$ tangoctl -h
$ ./src/ska_mid_itf_engineering_tools/tango_control/tangoctl.py -h
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
$ poetry install
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
Read Tango devices:

Display version number
        tangoctl --version

Display help
        tangoctl --help
        tangoctl -h

Display Kubernetes namespaces
        tangoctl --show-ns
        tangoctl -k

Display Tango database address
        tangoctl --show-db --k8s-ns=<NAMESPACE>
        tangoctl -t -K <NAMESPACE>
e.g. tangoctl -t -K integration

Display classes and Tango devices associated with them
        tangoctl -d|--class --k8s-ns=<NAMESPACE>|--host=<HOST>
        tangoctl -d|--class -K <NAMESPACE>|-H <HOST>
e.g. tangoctl -d -K integration

List Tango device names
        tangoctl --show-dev --k8s-ns=<NAMESPACE>|--host=<HOST>
        tangoctl -l -K <NAMESPACE>|-H <HOST>
e.g. tangoctl -l -K integration

Display all Tango devices (will take a long time)
        tangoctl --full|--short -e|--everything [--namespace=<NAMESPACE>|--host=<HOST>]
        tangoctl -l -K integration
        e.g. tangoctl -f|-s -K <NAMESPACE>|-H <HOST>

Filter on device name
        tangoctl --full|--short -D <DEVICE> -K <NAMESPACE>|-H <HOST>
        tangoctl -f|-s --device=<DEVICE> --k8s-ns=<NAMESPACE>|--host=<HOST>
e.g. tangoctl -f -K integration -D ska_mid/tm_leaf_node/csp_subarray01

Filter on attribute name
        tangoctl --full|--short --attribute=<ATTRIBUTE> --k8s-ns=<NAMESPACE>|--host=<HOST>
        tangoctl -f|-s -A <ATTRIBUTE> -K <NAMESPACE>|-H <HOST>
e.g. tangoctl -f -K integration -A timeout

Filter on command name
        tangoctl --full|--short --command=<COMMAND> --k8s-ns=<NAMESPACE>|--host=<HOST>
        tangoctl -f|-s -C <COMMAND> -K <NAMESPACE>|-H <HOST>
e.g. tangoctl -l -K integration -C status

Filter on property name
        tangoctl --full|--list|--short --property=<PROPERTY> --k8s-ns=<NAMESPACE>|--host=<HOST>
        tangoctl -f|-s -P <PROPERTY> --k8s-ns=<NAMESPACE>|--host=<HOST>
e.g. tangoctl -l -K integration -P power

Display tangoctl test input files
        tangoctl --json-dir=<PATH>
        tangoctl -J <PATH>
e.g. ADMIN_MODE=1 tangoctl -J resources/

Run test, reading from input file
        tangoctl --k8s-ns=<NAMESPACE> --input=<FILE>
        tangoctl --K <NAMESPACE> -O <FILE>
Files are in JSON format and contain values to be read and/or written, e.g:
{
    "description": "Turn admin mode on and check status",
    "test_on": [
        {
            "attribute": "adminMode",
            "read" : ""
        },
        {
            "attribute": "adminMode",
            "write": 1
        },
        {
            "attribute": "adminMode",
            "read": 1
        },
        {
            "command": "State",
            "return": "OFFLINE"
        },
        {
            "command": "Status"
        }
    ]
}  
    
Files can contain environment variables that are read at run-time:
{
    "description": "Turn admin mode off and check status",
    "test_on": [
        {
            "attribute": "adminMode",
            "read": ""
        },
        {
            "attribute": "adminMode",
            "write": "${ADMIN_MODE}"
        },
        {
            "attribute": "adminMode",
            "read": "${ADMIN_MODE}"
        },
        {
            "command": "State",
            "return": "ONLINE"
        },
        {
            "command": "Status"
        }
    ]    
}  
    
To run the above:
ADMIN_MODE=1 tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --in resources/dev_online.json -V

Test Tango devices:

Test a Tango device
        tangoctl -K <NAMESPACE>|-H <HOST> -D <DEVICE> [--simul=<0|1>]

Test a Tango device and read attributes
        tangoctl -a -K <NAMESPACE>|-H <HOST> -D <DEVICE> [--simul=<0|1>]

Display attribute and command names for a Tango device
        tangoctl -c -K <NAMESPACE>|-H <HOST> -D <DEVICE>

Turn a Tango device on
        tangoctl --on -K <NAMESPACE>|-H <HOST> -D <DEVICE> [--simul=<0|1>]

Turn a Tango device off
        tangoctl --off -K <NAMESPACE>|-H <HOST> -D <DEVICE> [--simul=<0|1>]

Set a Tango device to standby mode
        tangoctl --standby -K <NAMESPACE>|-H <HOST> -D <DEVICE> [--simul=<0|1>]

Change admin mode on a Tango device
        tangoctl --admin=<0|1>

Display status of a Tango device
        tangoctl --status -K <NAMESPACE>|-H <HOST> -D <DEVICE>

Check events for attribute of a Tango device
        tangoctl -K <NAMESPACE>|-H <HOST> -D <DEVICE> -A <ATTRIBUTE>

Parameters:

        -a                              flag for reading attributes during tests
        -c|--cmd                        flag for running commands during tests
        --simul=<0|1>                   set simulation mode off or on
        --admin=<0|1>                   set admin mode off or on
        -f|--full                       display in full
        -l|--list                       display device name and status on one line
        -s|--short                      display device name, status and query devices
        -q|--quiet                      do not display progress bars
        -j|--html                       output in HTML format
        -j|--json                       output in JSON format
        -m|--md                         output in markdown format
        -y|--yaml                       output in YAML format
        --json-dir=<PATH>               directory with JSON input file, e.g. 'resources'
        -J <PATH>
        --device=<DEVICE>               device name, e.g. 'csp' (not case sensitive, only a part is needed)
        -D <DEVICE>
        --k8s-ns=<NAMESPACE>            Kubernetes namespace for Tango database, e.g. 'integration'
        -K <NAMESPACE>
        --host=<HOST>                   Tango database host and port, e.g. 10.8.13.15:10000
        -H <HOST>
        --attribute=<ATTRIBUTE>         attribute name, e.g. 'obsState' (not case sensitive)
        -A <ATTRIBUTE>
        --command=<COMMAND>             command name, e.g. 'Status' (not case sensitive)
        -C <COMMAND>
        --output=<FILE>                 output file name
        -O <FILE>
        --input=<FILE>                  input file name
        -I <FILE>

Note that values for device, attribute, command or property are not case sensitive.
Partial matches for strings longer than 4 charaters are OK.

When a namespace is specified, the Tango database host will be made up as follows:
        tango-databaseds.<NAMESPACE>.miditf.internal.skao.int:10000

Run the following commands where applicable:
        QueryClass,QueryDevice,QuerySubDevice,GetVersionInfo,State,Status

Run commands with device name as parameter where applicable:
        DevLockStatus,DevPollStatus,GetLoggingTarget

Examples:

        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -l
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D talon -l
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -A timeout
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -C Telescope
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -P Power
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -f
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_lru/001 -q
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --dry
        tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid-sdp/control/0 --on
        ADMIN_MODE=1 tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --in resources/dev_online.json -V
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
$ tangoctl --namespace=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --dry-run
$ ADMIN_MODE=1 tangoctl --k8s-ns=ci-ska-mid-itf-at-1820-tmc-test-sdp-notebook-v2 -D mid_csp_cbf/talon_board/001 -f --in resources/dev_online.json -V
```
