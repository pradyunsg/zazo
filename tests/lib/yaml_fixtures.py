"""Helpers for YAML-file based tests
"""
# TODO: Decide the structure of the tests

import pytest
import yaml


class YAMLException(Exception):
    """Base for the exception hierarchy of this module
    """


class DoesNotMatch(YAMLException):
    """Raised when the result does not match the expected value
    """


class YamlFixtureFile(pytest.File):

    def collect(self):
        data = yaml.safe_load(self.fspath.open())
        print(data)


class YamlItem(pytest.Item):

    def __init__(self, name, parent, spec):
        # type: (str, Any, Any) -> None
        super(YamlItem, self).__init__(name, parent)
        self.spec = spec

    def runtest(self):
        # type: () -> None
        raise DoesNotMatch()

    # Called when the tests fail
    def repr_failure(self, excinfo):
        # type: (Any) -> str
        if isinstance(excinfo.value, DoesNotMatch):
            return "Test failed."

    def reportinfo(self):
        return self.fspath, 0, "yaml-test: %s" % self.name
