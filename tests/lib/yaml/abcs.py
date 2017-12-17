"""Contains a some helper implementations of zazo.abc classes
"""

from copy import deepcopy

from zazo.api import Candidate, Provider
from packaging.requirements import Requirement


class YAMLCandidate(Candidate):

    def __init__(self, name, version, dependencies):
        super(YAMLCandidate, self).__init__()
        self.name = name
        self.version = version
        assert isinstance(dependencies, dict), \
            "Mapping of extras to requirements"
        assert None in dependencies.keys(), "improper dependencies"

        self._dependencies = dependencies
        self.extras = set()

    def __repr__(self):
        return "YAMLCandidate('{} {}', extras={}, depends={})".format(
            self.name, self.version, self.extras, self._get_dependencies()
        )

    def _get_dependencies(self):
        num_of_extras = len(self.extras)

        if num_of_extras == 0:
            # There are no extras, return the top-level requirements
            return deepcopy(self._dependencies[None])
        elif num_of_extras == 1:
            extra_name = list(self.extras)[0]  # XXX: Check if this is _slow_?
            # We are "simple" extra requirement, depend on the matching package
            # name-version pair and extra dependencies.
            retval = [
                Requirement("{} == {}".format(self.name, self.version))
            ]
            if extra_name in self._dependencies:
                retval.extend(self._dependencies[extra_name])
            return retval
        else:
            # Short hands
            name = self.name
            version = self.version

            return [
                Requirement("{}[{}] == {}".format(name, extra_name, version))
                for extra_name in self.extras
            ]

    def matches(self, requirement):
        return (
            self.name == requirement.name and
            self.version in requirement.specifier and
            requirement.extras == self.extras
        )


class YAMLProvider(Provider):

    def __init__(self, data):
        super(YAMLProvider, self).__init__()
        self._candidates_by_name = data
        self._dependencies_by_candidate = data

    def get_candidates(self, requirement):
        try:
            candidates = deepcopy(self._candidates_by_name[requirement.name])
        except KeyError:
            return []

        for candidate in candidates:
            candidate.extras |= requirement.extras

        # TODO: Figure out a better way to do this
        return reversed(sorted(
            filter(lambda x: x.matches(requirement), candidates),
            key=lambda x: x.version
        ))

    def fetch_dependencies(self, candidate):
        # The reason we've ended up doing this is because of us loading and
        # storing dependency information in a candidate.
        return candidate._get_dependencies()
