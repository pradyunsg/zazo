"""Translation logic for structures from YAML
"""

from collections import defaultdict

from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import InvalidVersion, Version

from .abcs import YAMLCandidate
from .exceptions import AggregatedYAMLErrors, MalformedYAML, YAMLException


def translate_specification(test_id, specification):
    """We assume things that have been checked during the expansion.
    """
    index = specification["index"]
    actions = specification["actions"]
    results = specification["results"]

    retval = {}
    retval["candidates"], retval["dependencies"] = _translate_index(test_id, index)
    retval["subtests"] = _translate_actions_and_results(test_id, actions, results)

    return retval


def _translate_list(test_id, argument, name, function):
    retval = []

    errors = AggregatedYAMLErrors()
    for i, item in enumerate(argument):
        try:
            item = function(test_id, i, name, item)
        except YAMLException as e:
            errors.add(e)
        else:
            retval.append(item)

    if errors:
        raise errors

    return retval


def _translate_index(test_id, index):
    first_pass = _translate_list(test_id, index, "index", _translate_index_item)

    # Create a mapping of candidate data
    candidates = defaultdict(list)
    dependencies = {}

    # Error Checking
    errors = AggregatedYAMLErrors()
    for item in first_pass:
        candidate, new_deps = item
        already_specified = set(dependencies) & set(new_deps)
        if already_specified:
            # Nope. There's a problem.
            errors.add(
                MalformedYAML(
                    test_id,
                    "Got double specification for same candidate(s): {}",
                    already_specified,
                )
            )
        else:
            # Add the candidate and dependency information
            candidates[candidate.name].append(candidate)
            dependencies.update(new_deps)

    if errors:
        raise errors

    return dict(candidates), dependencies


def _translate_index_item(test_id, i, _, item):
    name = item["name"]
    try:
        version = Version(item["version"])
    except InvalidVersion:
        raise MalformedYAML(
            test_id, "index[{}] has an invalid version: {}", i, item["version"]
        )

    # Compose Dependencies
    dependencies = {}
    errors = AggregatedYAMLErrors()

    # Top level first.
    key = "{} {}".format(name, version)
    try:
        dependencies[key] = _translate_list(
            test_id, item["depends"], "index[{}], depends".format(i), function=_make_req
        )
    except YAMLException as e:
        errors.add(e)

    # Extras next.
    for extra in item["extras"]:
        key = "{}[{}] {}".format(name, extra, version)
        try:
            dependencies[key] = _translate_list(
                test_id,
                item["extras"][extra],
                "index[{}], extra={!r}".format(i, extra),
                function=_make_req,
            )
        except YAMLException as e:
            errors.add(e)

    if errors:
        raise errors

    return YAMLCandidate(name, version), dependencies


def _make_req(test_id, i, name, req_str):
    try:
        return Requirement(req_str)
    except InvalidRequirement as e:
        raise MalformedYAML(test_id, "{} has invalid requirement {!r}", name, req_str)


def _translate_actions_and_results(test_id, actions, results):
    return list(zip(actions, results))
