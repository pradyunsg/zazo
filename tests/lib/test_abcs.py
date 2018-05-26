"""Tests for the basic ABCs implemented.
"""

import pytest
from packaging.requirements import Requirement
from packaging.version import Version

from tests.lib.yaml.abcs import YAMLCandidate, YAMLProvider


# Shorthands for writing tests
def can(arg, extras=None):
    kwargs = {}
    kwargs["name"], kwargs["version"] = arg.split(" ")
    kwargs["version"] = Version(kwargs["version"])

    retval = YAMLCandidate(**kwargs)
    if extras is not None:
        retval.extras = set(extras)
    return retval


req = Requirement


# packaging's Requirements don't like being compared. Let's compare them by converting
# them into strings and comparing those.
def assert_requirements_match(requirements_1, requirements_2):
    assert all(isinstance(i, Requirement) for i in requirements_1)
    assert all(isinstance(i, Requirement) for i in requirements_2)

    requirements_strings_1 = sorted(str(i) for i in requirements_1)
    requirements_strings_2 = sorted(str(i) for i in requirements_2)

    assert requirements_strings_1 == requirements_strings_2


class TestCandidate(object):

    @pytest.mark.parametrize(
        ("candidate", "requirement", "should_match"),
        [
            ("A 1.0.0", "A", True),
            ("A 1.0.0", "A == 1.0.0", True),
            ("A 1.0.0", "A != 1.0.0", False),
        ],
    )
    def test_matches_correctly(self, candidate, requirement, should_match):
        if should_match:
            assert can(candidate).matches(req(requirement))
        else:
            assert not can(candidate).matches(req(requirement))

    @pytest.mark.parametrize(
        ("item1", "item2", "should_equal"),
        [
            ("A 1.0.0", "A 1.0.0", True),
            ("A 1.0.0", "B 1.0.0", False),  # diff name
            ("A 1.0.0", "A 2.0.0", False),  # diff ver
            ("A 1.0.0", "B 2.0.0", False),  # diff name and ver
        ],
    )
    def test_equality(self, item1, item2, should_equal):
        if should_equal:
            assert can(item1) == can(item2)
        else:
            assert can(item1) != can(item2)


class TestProvider(object):

    @pytest.mark.parametrize(
        ("candidate_info", "requirement", "expected"),
        [
            (
                {"A": [can("A 3.0.0"), can("A 2.0.0"), can("A 1.0.0")]},
                req("A"),
                [can("A 3.0.0"), can("A 2.0.0"), can("A 1.0.0")],
            ),
            (
                {"A": [can("A 3.0.0"), can("A 2.0.0"), can("A 1.0.0")]},
                req("A[extra]"),
                [
                    can("A 3.0.0", extras={"extra"}),
                    can("A 2.0.0", extras={"extra"}),
                    can("A 1.0.0", extras={"extra"}),
                ],
            ),
            (
                {"A": [can("A 1.0.0")], "B": [can("B 1.0.0")]},
                req("B"),
                [can("B 1.0.0")],
            ),
        ],
    )
    def test_gives_correct_candidates(self, candidate_info, requirement, expected):
        provider = YAMLProvider(candidate_info, {})

        assert provider.get_candidates(requirement) == expected

    @pytest.mark.parametrize(
        ("dependency_info", "requirement", "expected"),
        [
            (
                {
                    "A 2.0.0": [req("B")],
                    "A 1.0.0": [req("C")],
                    "A 0.2.0": [req("D")],
                    "A 0.1.0": [req("E")],
                },
                can("A 1.0.0"),
                [req("C")],
            ),
            (
                {
                    "A 2.0.0": [req("one")],
                    "A[doc] 2.0.0": [req("two")],
                    "A 1.0.0": [req("three")],
                    "A[doc] 1.0.0": [req("four")],
                },
                can("A 1.0.0", extras={"doc"}),
                [req("A == 1.0.0"), req("four")],
            ),
            (
                {
                    "A 1.0.0": [req("one")],
                    "A[doc] 1.0.0": [req("two")],
                    "A[test] 1.0.0": [req("three")],
                },
                can("A 1.0.0", extras={"doc", "test"}),
                [req("A[doc] == 1.0.0"), req("A[test] == 1.0.0")],
            ),
        ],
    )
    def test_gives_correct_dependencies(self, dependency_info, requirement, expected):
        provider = YAMLProvider({}, dependency_info)

        assert_requirements_match(provider.get_dependencies(requirement), expected)

    # TODO: Add tests for installation
    #       - double installs fail
    #       - extras on installation are modified correctly
    #       - extras installed are provided in returned candidate
    #       - version mismatch
    # TODO: Add tests for un-installation
    #       - refuses to uninstall stuff that's not installed
    #       - actually uninstalls stuff that's install
