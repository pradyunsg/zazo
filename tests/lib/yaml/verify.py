"""Helpers for converting between forms.

YAML -> (Candidates, Requirements) -> Error Messages
"""

from collections import defaultdict

from packaging.requirements import Requirement
from packaging.version import Version

from zazo.api import CannotSatisfy

from .exceptions import YAMLException


def _convert_error(result):
    return {"conflicts": []}


def _convert_resolved_set(result):
    retval = result.copy()
    for item in result:
        if "[" in item:
            del retval[item]
    # TODO: Make this do some actual restructuring
    return {"chosen_set": retval}


def verify_installation_result(result, expected):
    """Verify that an installation run did what it was supposed to.
    """

    if not isinstance(expected, dict):
        raise YAMLException("The expected result of this test is not a dictionary.")

    if isinstance(result, CannotSatisfy):
        result = _convert_error(result)
    else:
        result = _convert_resolved_set(result)

    errors = []
    if "conflicts" in expected:
        if "conflicts" not in result:
            message = "Expected to get conflicts, got resolved set"
            raise AssertionError(message)
        # TODO: Beef this up; maybe try to show what's messed up.
    else:
        assert "set" in expected, "set not in expected"
        if "chosen_set" not in result:
            message = "Expected to get resolved set, got conflicts"
            raise AssertionError(message)

        # Make sure we got the right versions
        for item in expected["set"]:
            name, version = item.split(" ", 1)
            if name not in result["chosen_set"]:
                errors.append(name + " is missing.")
                continue
            if Version(version) != result["chosen_set"][name].version:
                errors.append(
                    "Expected {} to be version {}, got {}".format(
                        name, version, result["chosen_set"][name].version
                    )
                )
            del result["chosen_set"][name]

        # Make sure we got the right packages
        if result["chosen_set"]:
            for key in result["chosen_set"]:
                errors.append(
                    "Got unexpected selection: {} {}".format(
                        key, result["chosen_set"][key].version
                    )
                )

        # TODO: Check the graph of dependencies

    if errors:
        raise IncorrectResolution(errors)
