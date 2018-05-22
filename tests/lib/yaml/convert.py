"""Helpers for converting between forms.

YAML -> (Candidates, Requirements) -> Error Messages
"""

from collections import defaultdict
from random import shuffle

from packaging.requirements import Requirement
from packaging.version import parse as parse_version

from zazo.api import CannotSatisfy

from .abcs import YAMLCandidate
from .exceptions import YAMLException


def _check_list(obj, name, content_type=None):
    assert isinstance(obj, list), name + "should be a list"
    if content_type is not None:
        assert all(isinstance(x, content_type) for x in obj), (
            "all items in " + name + " should be a " + content_type.__name__
        )


def _split_and_strip(my_str, splitwith, count=None):
    """Split a string and strip each component
    """
    if count is None:
        return [x.strip() for x in my_str.strip().split(splitwith)]
    else:
        return [x.strip() for x in my_str.strip().split(splitwith, count)]


def _make_req(string, item):
    try:
        return Requirement(string)
    except Exception:
        raise YAMLException("Could not parse requirement {!r} from {!r}", string, item)


def convert_index_string(item):
    if "depends " not in item:
        name_version = item
        depends = []
    else:
        name_version, depends_str = _split_and_strip(item, ";", 1)
        assert depends_str.startswith(
            "depends "
        ), "dependencies string must be specified with 'depends '"
        depends = _split_and_strip(depends_str[len("depends ") :], "&")

    name, version = _split_and_strip(name_version, " ", 1)
    version = parse_version(version)
    dependencies = {None: [_make_req(string, item) for string in depends]}

    return YAMLCandidate(name, version, dependencies)


def convert_index_dict(item):
    assert "name" in item, "index-item is not named"
    assert isinstance(item["name"], str), "index-item name is not a string"
    name = item["name"]

    assert "version" in item, "index-item is not versioned"
    assert isinstance(
        item["version"], str
    ), "index-item version is not a string"
    version = parse_version(item["version"])

    # This is where we store information about dependencies of a
    # package.
    dependencies = {None: []}

    if "depends" in item:
        assert isinstance(item["depends"], list) and all(
            isinstance(x, str) for x in item["depends"]
        ), "index-item depends should be a List[str]"
        dependencies[None] = [
            _make_req(string, item) for string in item["depends"]
        ]

    # If there are any extras, add information about them to the
    # dependencies dictionary.
    if "extras" in item:
        assert (
            isinstance(item["extras"], dict)
            and all(
                isinstance(x[0], str) and isinstance(x[1], list)
                for x in item["extras"].items()
            )
            and all(
                all(isinstance(y, str) for y in x)
                for x in item["extras"].values()
            )
        ), "index-item extras is not a Dict[str, List[str]]"

        for key, value in item["extras"].items():
            dependencies[key] = [_make_req(string, item) for string in value]

    return YAMLCandidate(name, version, dependencies)


def convert_index_to_candidates(index):
    assert isinstance(index, list), "index must be a list"

    # We will try to parse each item and update the corresponding entries in the
    # candidate and dependency mappings.
    candidates = {}
    dependencies = {}

    # Create the list of candidates
    retval = defaultdict(list)
    for item in index:
        if isinstance(item, str):
            candidate = convert_index_string(item)
        elif isinstance(item, dict):
            candidate = convert_index_dict(item)
        else:
            raise TypeError("Expected a string or dict.")
        retval[candidate.name].append(candidate)

    return retval


def _convert_error(result):
    return {"conflicts": []}


def _convert_resolved_set(result):
    retval = result.copy()
    for item in result:
        if "[" in item:
            del retval[item]
    # TODO: Make this do some actual restructuring
    return {"chosen_set": retval}


def convert_result_and_expected_and_check(result, expected):
    """Convert a single resolver-run result to match what was expected
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
            if parse_version(version) != result["chosen_set"][name].version:
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
        raise AssertionError("Incorrect resolution:\n- " + "\n- ".join(errors))
