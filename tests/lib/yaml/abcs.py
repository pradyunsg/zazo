"""Contains a some helper implementations of zazo.abc classes
"""

from copy import deepcopy

from packaging.requirements import Requirement

from zazo.api import Candidate, Provider


class YAMLCandidate(Candidate):

    def __init__(self, name, version):
        super(YAMLCandidate, self).__init__()
        self.name = name
        self.version = version

        self.extras = set()

    def __repr__(self):
        return "<YAMLCandidate({}[{}], {!r})>".format(
            self.name, ",".join(self.extras), self.version
        )

    def __eq__(self, other):
        return (
            self.name == other.name
            and self.version == other.version
            and self.extras == other.extras
        )

    def matches(self, requirement):
        return (
            self.name == requirement.name
            and self.extras == requirement.extras
            and self.version in requirement.specifier
        )


class YAMLProvider(Provider):

    def __init__(self, candidates, dependencies, installed=None):
        super(YAMLProvider, self).__init__()
        self._candidates_by_name = candidates
        self._dependencies_by_candidate = dependencies

        if installed is None:
            installed = {}

        self._installed = installed  # type: Dict[str, Tuple[Version, Extras]]

    def get_candidates(self, requirement):
        name = requirement.name

        # Make a copy of the candidates
        candidates = self._candidates_by_name.get(name, [])
        candidates = deepcopy(candidates)

        # Merge the extras
        for candidate in candidates:
            candidate.extras |= requirement.extras

        # NOTE: This is simply ordering the matching candidates in decreasing
        #       order of version. It only works in a case of installing in an
        #       empty (or equivalent) environment.
        return list(
            reversed(
                sorted(
                    filter(lambda x: x.matches(requirement), candidates),
                    key=lambda x: x.version,
                )
            )
        )

    def get_dependencies(self, candidate):
        # Short hands
        name = candidate.name
        version = candidate.version

        # Simple Requirement
        if not candidate.extras:
            return self._dependencies_by_candidate["{} {}".format(name, version)]
        # Single Extra (depends on parent + extra)
        elif len(candidate.extras) == 1:
            extra = next(iter(candidate.extras))

            # Add the parent package as the first requirement
            retval = [Requirement("{} == {}".format(name, version))]

            # Add the extra dependencies
            key = "{}[{}] {}".format(name, extra, version)
            retval.extend(self._dependencies_by_candidate.get(key, []))

            return retval
        # Multiple Extras (depends on all single extra variants)
        else:
            return [
                Requirement("{}[{}] == {}".format(name, extra_name, version))
                for extra_name in candidate.extras
            ]
