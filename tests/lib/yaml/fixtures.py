"""Helpers for YAML-file based tests
"""

from __future__ import absolute_import

import traceback

import pytest
import yaml
from packaging.requirements import InvalidRequirement, Requirement

from zazo.api import BackTrackingResolver, CannotSatisfy

from .abcs import YAMLProvider
from .exceptions import YAMLException
from .expand import expand_shorthands
from .translate import translate_specification
from .verify import verify_installation_result


class YamlFixtureItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlFixtureItem, self).__init__(name, parent)
        self.spec = spec

        self._actions = {
            "install": (self._do_install, self._check_install),
            "uninstall": (self._do_uninstall, self._check_uninstall),
        }

    # Called when the tests fail
    def repr_failure(self, excinfo):
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

    def runtest(self):
        # Convert things into something usable.
        expanded_spec = expand_shorthands(self.name, self.spec)
        test_spec = translate_specification(self.name, expanded_spec)

        # Create a Provider, using information
        provider = YAMLProvider(test_spec["candidates"], test_spec["dependencies"])

        for action, expected in test_spec["subtests"]:
            result = self._perform_action(action, provider)
            self._check_action_result(action, result, expected)

    ###### Helpers ######
    def _perform_action(self, action, provider):
        verb = action["action"]
        func = getattr(self, "_do_" + verb, None)
        if func is None:
            raise Exception("Can not perform verb {!r}.".format(verb))

        return func(provider, action)

    def _check_action_result(self, action, result, expected):
        verb = action["action"]
        func = getattr(self, "_check_" + verb, None)
        if func is None:
            raise Exception("Can not check verb {!r}.".format(verb))

        func(result, expected)

    ###### Actions ######
    def _do_uninstall(self, provider, names):
        # _check_list(names, "uninstall items", str)
        provider.uninstall_names(names)

    def _check_uninstall(self, result, expected):
        assert result is None
        assert expected == "tada"

    def _do_install_prepare_reqs(self, action):
        """Create a list of requirements from given items.
        """

        def _make_req(string):
            try:
                return Requirement(string)
            except Exception:
                raise YAMLException(
                    "Could not parse requirement {!r} from {!r}",
                    string,
                    action["items"],
                )

        return [_make_req(r) for r in action["items"]]

    def _do_install(self, provider, items):
        """Compose a list of requirements and then run the resolver to install them.
        """
        requirements = self._do_install_prepare_reqs(items)
        result = self._run_resolver(requirements, provider)

        return result

    def _check_install(self, result, expected):
        verify_installation_result(result, expected)

    def _run_resolver(self, requirements, provider):
        resolver = BackTrackingResolver(provider)
        try:
            to_install = resolver.resolve(requirements)
        except CannotSatisfy as e:
            return e
        else:
            return to_install


class YamlFixtureFile(pytest.File):
    def _compose_tests(self, data):
        # _check_list(data, "test data")
        for i, item in enumerate(data):
            name = "{}[{}]".format(self.fspath.basename, i)
            yield YamlFixtureItem(name, self, item)

    def collect(self):
        loader = yaml.CLoader if hasattr(yaml, "CLoader") else yaml.Loader
        with self.fspath.open() as f:
            data = yaml.load(f.read(), Loader=loader)
        for test in self._compose_tests(data):
            yield test
