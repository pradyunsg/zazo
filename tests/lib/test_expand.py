"""Test various expansions
"""

import pytest

from tests.lib.yaml import expand
from tests.lib.yaml.exceptions import MalformedYAML


@pytest.mark.parametrize(
    "di",
    [
        {},
        {"index": None},
        {"actions": None},
        {"results": None},
        {"index": None, "actions": None},
        {"index": None, "results": None},
        {"actions": None, "results": None},
        {"index": None, "actions": None, "results": None, "hello": None},
    ],
)
def test_fails_when_top_level_structure_is_incorrect(di):
    with pytest.raises(MalformedYAML) as err:
        expand.expand_shorthands(0, di)

    assert "top-level has incorrect structure" in str(err)


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("A 1.0.0", {"name": "A", "version": "1.0.0", "depends": [], "extras": {}}),
        (
            "A 1.0.0 depends B == 1.0.0 & C",
            {
                "name": "A",
                "version": "1.0.0",
                "depends": ["B == 1.0.0", "C"],
                "extras": {},
            },
        ),
    ],
)
def test_expand_index_string(string, expected):
    assert expand._expand_index_item_string(0, 0, string) == expected


@pytest.mark.parametrize(
    ("string", "expected_words"),
    [
        ("A", "does not specify name and version correctly"),
        ("A depends B", "does not specify name and version correctly"),
        ("A 1.0.0 depends", "does not specify 'depends' correctly"),
    ],
)
def test_expand_index_string_errors(string, expected_words):
    with pytest.raises(MalformedYAML) as err:
        expand._expand_index_item_string(0, 0, string)

    assert expected_words in str(err)


@pytest.mark.parametrize(
    "item",
    [
        # Wrong Keys
        {"name": "A", "version": "1.0.0"},
        {"name": "A", "version": "1.0.0", "depends": []},
        {"name": "A", "version": "1.0.0", "depends": [], "extras": []},
        # Incorrect types
        {"name": "A", "version": "1.0.0", "depends": [], "extras": []},
        {"name": "A", "version": "1.0.0", "depends": {}, "extras": {}},
        {"name": ["A"], "version": "1.0.0", "depends": [], "extras": {}},
        {"name": "A", "version": ["1.0.0"], "depends": [], "extras": {}},
        {"name": "A", "version": "1.0.0", "depends": [1], "extras": {}},
        {"name": "A", "version": "1.0.0", "depends": [1], "extras": {}},
        {"name": "A", "version": "1.0.0", "depends": [], "extras": {1: []}},
        {"name": "A", "version": "1.0.0", "depends": [], "extras": {"str": [1]}},
    ],
)
def test_expand_index_item_errors(item):
    with pytest.raises(MalformedYAML) as err:
        expand._expand_index_item(0, 0, item)

    assert "index[0] has incorrect structure" in str(err)


@pytest.mark.parametrize(
    ("di", "expected"),
    [
        ({"install": [1, 2, 3]}, {"action": "install", "items": [1, 2, 3]}),
        ({"action": "abcd", "items": "efgh"}, {"action": "abcd", "items": "efgh"}),
    ],
)
def test_expand_action_dict(di, expected):
    assert expand._expand_action_item_dict(0, 0, di) == expected


@pytest.mark.parametrize(
    ("di", "expected_words"),
    [
        ({}, "empty dictionary"),
        ({"action": "abcd"}, "has an 'action' but no 'items'"),
        ({"blah": "abcd", "foo": "efgh"}, "incorrect dictionary"),
    ],
)
def test_expand_action_dict_errors(di, expected_words):
    with pytest.raises(MalformedYAML) as err:
        expand._expand_action_item_dict(0, 0, di)

    assert expected_words in str(err)


@pytest.mark.parametrize(
    ("di", "expected"),
    [
        ({"foo": "bar"}, {"foo": "bar"}),
        ({"set": "abcd", "graph": "efgh"}, {"set": "abcd", "graph": "efgh"}),
    ],
)
def test_expand_result_dict(di, expected):
    assert expand._expand_result_item_dict(0, 0, di) == expected


@pytest.mark.parametrize(
    ("di", "expected_words"),
    [
        ({}, "empty dictionary"),
        ({"set": []}, "has a 'set' but no 'graph'"),
        ({"graph": []}, "has a 'graph' but no 'set'"),
    ],
)
def test_expand_result_dict_errors(di, expected_words):
    with pytest.raises(MalformedYAML) as err:
        expand._expand_result_item_dict(0, 0, di)

    assert expected_words in str(err)


def test_expand_valid():
    pass
