"""Helpers for YAML-file based tests
"""

from __future__ import absolute_import

import traceback

import yaml
import pytest
from packaging.requirements import Requirement

from .abcs import YAMLProvider
from .convert import (
    convert_index_to_candidates, convert_result_and_expected_and_check
)
from .exceptions import YAMLException
from zazo.api import BackTrackingResolver, CannotSatisfy


class YamlFixtureItem(pytest.Item):

    def __init__(self, name, parent, spec):
        # type: (str, Any, Any) -> None
        super(YamlFixtureItem, self).__init__(name, parent)
        self.spec = spec

    def _compose_requirements(self):
        assert isinstance(self.spec["actions"], list)
        assert isinstance(self.spec["results"], list)
        for action, result in zip(self.spec["actions"], self.spec["results"]):

            assert isinstance(action, dict)
            assert len(action) == 1

            verb = list(action.keys())[0]
            # FIXME: install, upgrade, uninstall are things we care about
            assert verb == "install", "Unknown verb {}".format(verb)

            req_str_list = action[verb]
            if isinstance(req_str_list, str):
                req_str_list = [req_str_list]
            assert isinstance(req_str_list, list)
            requirements = [Requirement(r) for r in req_str_list]

            yield requirements, result

    def runtest(self):
        assert isinstance(self.spec, dict)
        assert "index" in self.spec
        assert "actions" in self.spec
        assert "results" in self.spec

        # Create a Provider, using index
        provider = YAMLProvider(
            convert_index_to_candidates(self.spec["index"])
        )

        for requirements, expected in self._compose_requirements():
            # Actual Testing Code
            resolver = BackTrackingResolver(provider)
            try:
                result = resolver.resolve(requirements)
            except CannotSatisfy as e:
                result = e

            convert_result_and_expected_and_check(result, expected)

    # Called when the tests fail
    def repr_failure(self, excinfo):
        # type: (Any) -> str
        if isinstance(excinfo.value, YAMLException):
            # Format a reason
            if not excinfo.value.args:
                message = "unknown"
            else:
                if len(excinfo.value.args) == 1:
                    message = excinfo.value.args[0]
                else:
                    try:
                        message = excinfo.value.args[0].format(
                            excinfo.value.args[1:]
                        )
                    except Exception:
                        message = "Unable to format message: " + str(
                            excinfo.value.args
                        )
            # Print the reason
            return "YAML is malformed -- reason: {}".format(message)
        elif isinstance(excinfo.value, AssertionError):
            msg = (": " + excinfo.value.args[0]) if excinfo.value.args else ""
            return "assertion failed" + msg
        else:
            trace = traceback.format_exception(
                excinfo.type, excinfo.value, excinfo.tb
            )
            return "".join(trace) + "\nError occurred."

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
            data = yaml.load(f.read(), Loader=yaml.CLoader)
        for test in self._compose_tests(data):
            yield test
