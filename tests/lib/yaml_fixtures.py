"""Helpers for YAML-file based tests
"""
# TODO: Decide the structure of the tests

import pytest
import yaml


class YAMLException(Exception):
    """Base for the exception hierarchy of this module
    """


class YamlFixtureItem(pytest.Item):

    def __init__(self, name, parent, spec):
        # type: (str, Any, Any) -> None
        super(YamlFixtureItem, self).__init__(name, parent)
        self.spec = spec

    def runtest(self):
        # type: () -> None
        raise YAMLException("no-op test")

    # Called when the tests fail
    def repr_failure(self, excinfo):
        # type: (Any) -> str
        if isinstance(excinfo.value, YAMLException):
            if excinfo.value.args:
                message = excinfo.value.args[0]
                arguments = excinfo.value.args[1:]
            else:
                message = "unknown"
                arguments = ()
            return "Test failed; reason: {}".format(message.format(*arguments))

    def reportinfo(self):
        return self.fspath, 0, "yaml-test: %s" % self.name


class YamlFixtureFile(pytest.File):

    def _compose_tests(self, data):
        assert isinstance(data, list)
        for i, item in enumerate(data):
            name = "{}[{}]".format(self.fspath.basename, i)
            yield YamlFixtureItem(name, self, item)

    def collect(self):
        with self.fspath.open() as f:
            data = yaml.safe_load(f)
        for test in self._compose_tests(data):
            yield test
