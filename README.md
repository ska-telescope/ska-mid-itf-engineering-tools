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
