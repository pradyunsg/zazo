"""Contains a some helper implementations of zazo.abc classes
"""

from copy import deepcopy

from zazo.api import Candidate, Provider


class YAMLCandidate(Candidate):

    def __init__(self, name, version, dependencies):
        super(YAMLCandidate, self).__init__()
        self.name = name
        self.version = version
        assert isinstance(dependencies, dict), \
            "Mapping of extras to requirements"
        assert None in dependencies.keys()
        self._dependencies = dependencies
        # self._extras_requested = set()

    def __repr__(self):
        return "YAMLCandidate(name={!r}, version={}, dependecies={})".format(
            self.name, self.version, self._dependencies
        )

    # def _add_extras_requested(self, other_extras):
    #     self._extras_requested |= set(other_extras)

    def matches(self, requirement):
        return (
            self.name == requirement.name and
            self.version in requirement.specifier
            # and all(e in self._extras_requested for e in requirement.extras)
        )


class YAMLProvider(Provider):

    def __init__(self, data):
        super(YAMLProvider, self).__init__()
        self._candidates_by_name = data

    def get_candidates(self, requirement):
        try:
            candidates = self._candidates_by_name[requirement.name]
        except KeyError:
            return []

        return sorted(
            filter(lambda x: x.matches(requirement), candidates),
            key=lambda x: x.version
        )[::-1]

    def fetch_dependencies(self, candidate):
        retval = candidate._dependencies[None]

        # for extra in candidate._extras_requested:
        #     if extra not in candidate._dependencies:
        #         continue

        #     items = deepcopy(candidate._dependencies[extra])
        #     for item in items:
        #         item.extras = item.extras.union(candidate._extras_requested)
        #     retval.extend(items)

        return retval
