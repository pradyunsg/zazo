"""Expansion logic for shorthands in YAML.
"""

from .exceptions import AggregatedYAMLErrors, MalformedYAML, YAMLException


def expand_shorthands(test_id, test_dict):
    """Expands all the shorthands to the "expanded" form.

    This simplifies the rest of the code by eliminating the need for them to handle
    shorthands and basic sanity checks.
    """

    _ensure_keys(
        test_id, "top-level", test_dict, {"name", "actions", "index", "results"}
    )

    # Expand everything.
    index = _expand_index(test_id, test_dict["index"])
    actions = _expand_actions(test_id, test_dict["actions"])
    results = _expand_results(test_id, test_dict["results"])

    return {"index": index, "actions": actions, "results": results}


def _ensure_keys(test_id, level, di, expected_keys):
    actual_keys = set(di.keys())
    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)

        parts = []
        if missing:
            parts.append("(have missing: " + str(missing)[1:-1] + ")")
        if extra:
            parts.append("(got extra: " + str(extra)[1:-1] + ")")

        raise MalformedYAML(
            test_id, "{} has incorrect structure: {}", level, " ".join(parts)
        )


def _meta_expand(test_id, argument, name, function):
    if not isinstance(argument, list):
        raise MalformedYAML(test_id, "has a non-list " + name)

    errors = AggregatedYAMLErrors()
    for i, item in enumerate(argument):
        try:
            item = function(test_id, i, item)
        except YAMLException as e:
            errors.add(e)
        else:
            # Substitute with the changed item.
            argument[i] = item

    if errors:
        raise errors

    return argument


def _expand_index(test_id, index):
    return _meta_expand(test_id, index, "index", _expand_index_item)


def _expand_index_item(test_id, i, item):
    if isinstance(item, str):
        item = _expand_index_item_string(test_id, i, item)
    elif isinstance(item, dict):
        pass
    else:
        raise MalformedYAML(test_id, "index[{}] is incorrect: {!r}", i, item)

    _ensure_keys(
        test_id, "index[{}]".format(i), item, {"name", "version", "depends", "extras"}
    )
    if not (
        isinstance(item["name"], str)
        and isinstance(item["version"], str)
        and isinstance(item["depends"], list)
        and all(isinstance(obj, str) for obj in item["depends"])
        and isinstance(item["extras"], dict)
        and all(isinstance(obj, str) for obj in item["extras"].keys())
        and all(isinstance(obj, list) for obj in item["extras"].values())
        and all(
            isinstance(elem, str) for obj in item["extras"].values() for elem in obj
        )
    ):
        raise MalformedYAML(test_id, "index[{}] has incorrect structure.", i)

    return item


def _expand_index_item_string(test_id, i, item):
    """Expand an item in the index, which is a string.
    """

    def _split_and_strip(my_str, splitwith, count=None):
        """Split a string and strip each component
        """
        if count is None:
            return [x.strip() for x in my_str.strip().split(splitwith)]
        else:
            return [x.strip() for x in my_str.strip().split(splitwith, count)]

    # Super Cautious Checking of depends.
    if "depends" in item:  # this could be wrong but eh. Will deal with that later.
        errored = False
        try:
            name_version, depends_str = _split_and_strip(item, " depends ", 1)
            depends_str = _split_and_strip(depends_str, "&")
        except ValueError:
            errored = True

        if errored:
            raise MalformedYAML(
                test_id, "index[{}] does not specify 'depends' correctly", i
            )
    else:
        name_version = item
        depends_str = []

    try:
        name, version = _split_and_strip(name_version, " ", 1)
    except ValueError:
        raise MalformedYAML(
            test_id, "index[{}] does not specify name and version correctly", i
        )

    return {"name": name, "version": version, "depends": depends_str, "extras": {}}


def _expand_actions(test_id, actions):
    return _meta_expand(test_id, actions, "actions", _expand_action_item)


def _expand_action_item(test_id, i, item):
    if isinstance(item, dict):
        return _expand_action_item_dict(test_id, i, item)
    else:
        raise MalformedYAML(test_id, "actions[{}] is not a dictionary: {!r}", i, item)


def _expand_action_item_dict(test_id, i, item):
    if not item:
        raise MalformedYAML(test_id, "actions[{}] is an empty dictionary.", i)
    elif "action" in item:
        if "items" not in item:
            raise MalformedYAML(
                test_id, "actions[{}] has an 'action' but no 'items'.", i
            )
        return item  # We'll validate later.
    elif len(item) == 1:
        # convert {"install": ...} -> {"action": "install", "items": ...}
        key, value = next(iter(item.items()))
        return {"action": key, "items": value}
    else:
        raise MalformedYAML(test_id, "actions[{}] is an incorrect dictionary.", i)


def _expand_results(test_id, results):
    return _meta_expand(test_id, results, "results", _expand_result_item)


def _expand_result_item(test_id, i, item):
    if isinstance(item, dict):
        return _expand_result_item_dict(test_id, i, item)
    else:
        raise MalformedYAML(test_id, "results[{}] is not a dictionary.", i)


def _expand_result_item_dict(test_id, i, item):
    if not item:
        raise MalformedYAML(test_id, "results[{}] is an empty dictionary.", i)

    if "set" in item and "graph" not in item:
        raise MalformedYAML(test_id, "results[{}] has a 'set' but no 'graph'.", i)
    elif "graph" in item and "set" not in item:
        raise MalformedYAML(test_id, "results[{}] has a 'graph' but no 'set'.", i)

    return item
