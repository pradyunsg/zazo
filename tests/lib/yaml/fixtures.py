"""Helpers for YAML-file based tests
"""

from __future__ import absolute_import

import traceback

import pytest
import yaml
from packaging.requirements import InvalidRequirement, Requirement

from zazo.api import BackTrackingResolver, CannotSatisfy

from .abcs import YAMLProvider
from .convert import convert_index_to_candidates, convert_result_and_expected_and_check
from .exceptions import YAMLException


class YamlFixtureItem(pytest.Item):

    def __init__(self, name, parent, spec):
        # type: (str, Any, Any) -> None
        super(YamlFixtureItem, self).__init__(name, parent)
        self.spec = spec

    def _compose_requirements(self):
        assert isinstance(self.spec["actions"], list), "actions should be a list"
        assert isinstance(self.spec["results"], list), "results should be a list"

        for action, result in zip(self.spec["actions"], self.spec["results"]):
            assert isinstance(action, dict), "an action should be a dict"
            assert len(action) == 1, "an action should have a single item"

            verb = list(action.keys())[0]
            # FIXME: install, upgrade, uninstall are things we care about
            assert verb == "install", "Unknown verb {}".format(verb)

            req_str_list = action[verb]
            if isinstance(req_str_list, str):
                req_str_list = [req_str_list]
            assert (
                isinstance(req_str_list, list)
                and all(isinstance(x, str) for x in req_str_list)
            ), "requirements should be a string or list of strings"

            try:
                requirements = [Requirement(r) for r in req_str_list]
            except InvalidRequirement:
                raise YAMLException("Got invalid requirement in {}", req_str_list)
            yield requirements, result

    def runtest(self):
        assert isinstance(self.spec, dict), "a test should be a dictionary"
        assert "index" in self.spec, "there should be index in a test"
        assert "actions" in self.spec, "there should be actions in a test"
        assert "results" in self.spec, "there should be results in a test"

        # Create a Provider, using index
        provider = YAMLProvider(convert_index_to_candidates(self.spec["index"]))

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
            elif len(excinfo.value.args) == 1:
                message = excinfo.value.args[0]
            else:
                try:
                    message = excinfo.value.args[0].format(*excinfo.value.args[1:])
                except Exception as error:
                    message = "Unable to format message: {}\n{}".format(
                        excinfo.value.args, error
                    )
            # Print the reason
            return "YAML is malformed -- reason: {}".format(message)
        elif isinstance(excinfo.value, AssertionError):
            if excinfo.value.args:
                msg = ": " + str(excinfo.value.args[0])
            else:
                msg = ""
            return "assertion failed" + msg
        else:
            trace = traceback.format_exception(excinfo.type, excinfo.value, excinfo.tb)
            return "".join(trace) + "\nError occurred."

    def reportinfo(self):
        return self.fspath, 0, "yaml-test: %s" % self.name


class YamlFixtureFile(pytest.File):

    def _compose_tests(self, data):
        assert isinstance(data, list), "test data should be a list"
        for i, item in enumerate(data):
            name = "{}[{}]".format(self.fspath.basename, i)
            yield YamlFixtureItem(name, self, item)

    def collect(self):
        loader = yaml.CLoader if hasattr(yaml, "CLoader") else yaml.Loader
        with self.fspath.open() as f:
            data = yaml.load(f.read(), Loader=loader)
        for test in self._compose_tests(data):
            yield test
