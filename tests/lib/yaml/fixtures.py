"""Helpers for YAML-file based tests
"""

from __future__ import absolute_import

import traceback

import pytest
import yaml
from packaging.requirements import InvalidRequirement, Requirement

from zazo.api import BackTrackingResolver, CannotSatisfy

from .abcs import YAMLProvider
from .convert import (
    convert_index_to_candidates, convert_result_and_expected_and_check,
    _check_list
)
from .exceptions import YAMLException


class YamlFixtureItem(pytest.Item):

    def __init__(self, name, parent, spec):
        # type: (str, Any, Any) -> None
        super(YamlFixtureItem, self).__init__(name, parent)
        self.spec = spec

    def _compose_install_requirements(self, req_str_list):
        if isinstance(req_str_list, str):
            req_str_list = [req_str_list]

        _check_list(req_str_list, "install:", str)

        try:
            requirements = [Requirement(r) for r in req_str_list]
        except InvalidRequirement:
            raise YAMLException("Got invalid requirement in {}", req_str_list)

        return requirements

    def _compose_requirements(self):
        _check_list(self.spec["actions"], "actions")
        _check_list(self.spec["results"], "results")

        for action, result in zip(self.spec["actions"], self.spec["results"]):
            assert isinstance(action, dict), "an action should be a dict"
            assert len(action) == 1, "an action should have a single item"

            verb = list(action.keys())[0]
            if verb == "install":
                yield (
                    self._compose_install_requirements(action[verb]),
                    result
                )
            else:
                raise Exception("Unknown verb.")

    def runtest(self):
        assert isinstance(self.spec, dict), "a test should be a dictionary"
        assert "index" in self.spec, "there should be index in a test"
        assert "actions" in self.spec, "there should be actions in a test"
        assert "results" in self.spec, "there should be results in a test"

        # Create a Provider, using index
        provider = YAMLProvider(convert_index_to_candidates(self.spec["index"]))
        for requirements, expected in self._compose_requirements():
            result = self._run(requirements, provider)
            convert_result_and_expected_and_check(result, expected)

    def _run(self, requirements, provider):
        resolver = BackTrackingResolver(provider)
        try:
            result = resolver.resolve(requirements)
        except CannotSatisfy as e:
            result = e
        return result

    # Called when the tests fail
    def repr_failure(self, excinfo):
        # type: (Any) -> str
        error = excinfo.value
        if isinstance(error, YAMLException):
            return str(error)
        elif isinstance(error, AssertionError):
            msg = ": {}".format(error.args[0]) if error.args else ""
            return "assertion failed" + msg
        else:
            trace = traceback.format_exception(excinfo.type, excinfo.value, excinfo.tb)
            return "".join(trace) + "\nError occurred."

    def reportinfo(self):
        return self.fspath, 0, "yaml-test: %s" % self.name


class YamlFixtureFile(pytest.File):

    def _compose_tests(self, data):
        _check_list(data, "test data")
        for i, item in enumerate(data):
            name = "{}[{}]".format(self.fspath.basename, i)
            yield YamlFixtureItem(name, self, item)

    def collect(self):
        loader = yaml.CLoader if hasattr(yaml, "CLoader") else yaml.Loader
        with self.fspath.open() as f:
            data = yaml.load(f.read(), Loader=loader)
        for test in self._compose_tests(data):
            yield test
