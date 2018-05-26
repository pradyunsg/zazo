"""Tests for translation of expansions into actual objects for the Provider.
"""

import pytest
from packaging.requirements import Requirement as _Requirement
from packaging.version import Version

from tests.lib.yaml import translate
from tests.lib.yaml.abcs import YAMLCandidate
from tests.lib.yaml.exceptions import MalformedYAML, YAMLException


# XXX: This is a hack for working around the fact that packaging's Requirement doesn't
#      have equality checking.
class Requirement(_Requirement):

    def __eq__(self, other):
        return str(self) == str(other)


def test_translate_specification():
    spec = {
        "index": [
            {
                "name": "A",
                "version": "1.0.0",
                "depends": ["six"],
                "extras": {"docs": ["Sphinx"]},
            }
        ],
        "actions": [{"action": "install", "items": "A"}],
        "results": [{"set": ["A 1.0.0"], "graph": []}],
    }
    expected = {
        "candidates": {"A": [YAMLCandidate("A", Version("1.0.0"))]},
        "dependencies": {
            "A 1.0.0": [Requirement("six")],
            "A[docs] 1.0.0": [Requirement("Sphinx")],
        },
        "subtests": [
            ({"action": "install", "items": "A"}, {"set": ["A 1.0.0"], "graph": []})
        ],
    }
    got = translate.translate_specification(0, spec)

    assert expected == got


def test_index_double_specification():
    with pytest.raises(YAMLException) as e:
        translate._translate_index(
            0,
            [
                {"name": "A", "version": "1.0.0", "depends": [], "extras": {}},
                {"name": "A", "version": "1.0.0", "depends": [], "extras": {}},
            ],
        )

    assert "double specification" in str(e)


@pytest.mark.parametrize(
    ("message", "item"),
    [
        (
            "invalid version",
            {"name": "A", "version": "foo", "depends": [], "extras": {}},
        ),
        (
            "depends has invalid requirement",
            {"name": "A", "version": "1.0.0", "depends": ["..."], "extras": {}},
        ),
        (
            "extra='tada' has invalid requirement",
            {
                "name": "A",
                "version": "1.0.0",
                "depends": [],
                "extras": {"tada": ["..."]},
            },
        ),
    ],
)
def test_index_item_errors(item, message):
    with pytest.raises(YAMLException) as e:
        translate._translate_index_item(0, 0, None, item)

    assert message in str(e)
