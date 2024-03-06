"""Tests for the Helm dependency collector."""

from typing import List

import pytest

from ska_mid_itf_engineering_tools.dependency_checker import helm_dependency_collector
from ska_mid_itf_engineering_tools.dependency_checker.types import Dependency


@pytest.fixture(name="helm_output_valid")
def fixture_helm_output_valid() -> str:
    """
    Return the valid 'helm dependency list' output.

    :return: The valid output string.
    :rtype: str
    """
    return """NAME                    VERSION REPOSITORY    STATUS
ska-tango-base          0.4.9   https://artefact.skao.int/repository/helm-internal      ok
ska-tango-util          0.4.10  https://artefact.skao.int/repository/helm-internal      ok
ska-tmc-mid             0.15.7  https://artefact.skao.int/repository/helm-internal      ok
ska-csp-lmc-mid         0.18.2  https://artefact.skao.int/repository/helm-internal      ok
ska-mid-cbf-mcs         0.12.18 https://artefact.skao.int/repository/helm-internal      ok
ska-sdp                 0.18.1  https://artefact.skao.int/repository/helm-internal      ok
ska-tango-taranta       2.7.2   https://artefact.skao.int/repository/helm-internal      ok
ska-tango-tangogql      1.3.10  https://artefact.skao.int/repository/helm-internal      ok
ska-log-consumer        0.1.6   https://artefact.skao.int/repository/helm-internal      ok
ska-tango-alarmhandler  0.4.0   https://artefact.skao.int/repository/helm-internal      ok
ska-tango-archiver      2.7.0   https://artefact.skao.int/repository/helm-internal      ok

WARNING: "charts/system-under-test/charts/test-0.12.2.tgz" is not in Chart.yaml."""


@pytest.fixture(name="helm_output_invalid")
def fixture_helm_output_invalid() -> str:
    """
    Return the invalid 'helm dependency list' output.

    :return: The invalid output string.
    :rtype: str
    """
    return """NAME                    VERSION REPOSITORY    STATUS
ska-tango-base          0.4.9   https://artefact.skao.int/repository/helm-internal      ok

ska-tmc-mid
ska-tango-util          https://artefact.skao.int/repository/helm-internal      wrong version

WARNING: "charts/system-under-test/charts/test-0.12.2.tgz" is not in Chart.yaml."""


@pytest.fixture(name="helm_dependencies_valid")
def fixture_helm_dependencies_valid() -> List[Dependency]:
    """
    Return the expected valid dependencies.

    :return: List of the the expected valid dependencies.
    :rtype: List[Dependency]
    """
    return [
        Dependency(name="ska-tango-base", project_version="0.4.9", available_version="0.4.9"),
        Dependency(name="ska-tango-util", project_version="0.4.10", available_version="0.4.10"),
        Dependency(name="ska-tmc-mid", project_version="0.15.7", available_version="0.15.7"),
        Dependency(name="ska-csp-lmc-mid", project_version="0.18.2", available_version="0.18.2"),
        Dependency(name="ska-mid-cbf-mcs", project_version="0.12.18", available_version="0.12.18"),
        Dependency(name="ska-sdp", project_version="0.18.1", available_version="0.18.1"),
        Dependency(name="ska-tango-taranta", project_version="2.7.2", available_version="2.7.2"),
        Dependency(
            name="ska-tango-tangogql", project_version="1.3.10", available_version="1.3.10"
        ),
        Dependency(name="ska-log-consumer", project_version="0.1.6", available_version="0.1.6"),
        Dependency(
            name="ska-tango-alarmhandler", project_version="0.4.0", available_version="0.4.0"
        ),
        Dependency(name="ska-tango-archiver", project_version="2.7.0", available_version="2.7.0"),
    ]


def test_parse_helm_valid(helm_output_valid: str, helm_dependencies_valid: List[Dependency]):
    """
    Tests that valid helm output is parsed correctly.

    :param helm_output_valid: The output to parse
    :type helm_output_valid: str
    :param helm_dependencies_valid: The expected results
    :type helm_dependencies_valid: List[Dependency]
    """
    dc = helm_dependency_collector.HelmDependencyCollector()
    result = dc.parse_helm_dependencies(helm_output_valid)
    assert result == helm_dependencies_valid


def test_parse_helm_empty():
    """Tests that valid helm output is parsed correctly."""
    dc = helm_dependency_collector.HelmDependencyCollector()
    result = dc.parse_helm_dependencies("")
    assert result == []


def test_parse_helm_invalid(helm_output_invalid: str):
    """
    Tests that invalid helm output is parsed correctly.

    :param helm_output_invalid: The output to parse
    :type helm_output_invalid: str
    """
    with pytest.raises(ValueError):
        dc = helm_dependency_collector.HelmDependencyCollector()
        dc.parse_helm_dependencies(helm_output_invalid)
