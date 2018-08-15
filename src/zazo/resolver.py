"""
"""

import inspect
import logging

from .exceptions import CannotSatisfy

if False:
    from typing import Any, List, Dict  # noqa
    from packaging.requirements import Requirement  # noqa
    from zazo.abc import Provider, Candidate  # noqa

    Graph = Dict[str, Candidate]

logger = logging.getLogger()


def _create_key(req):
    # type: (Requirement) -> str
    parts = [req.name]  # type: List[str]

    if req.extras:
        parts.append("[{0}]".format(",".join(sorted(req.extras))))

    return "".join(parts)


class BackTrackingResolver(object):
    def __init__(self, provider):
        # type: (Provider) -> None
        super(BackTrackingResolver, self).__init__()
        self.provider = provider

    def resolve(self, requirements):
        # type: (List[Requirement]) -> Graph
        self._initial_recursion_depth = len(inspect.stack())
        graph = {}  # type: Graph
        try:
            # The following involves a speedup hack.
            retval = self._resolve(requirements, graph)
        except CannotSatisfy:
            logger.debug("Unable to satisfy dependencies.")
            raise
        else:
            logger.debug("Found satisfying set: %s", retval)
            return retval

    # TODO: Figure out feasibility of blacklisting of known conflicts, like
    #       Stork.
    def _resolve(self, requirements, graph):
        # type: (List[Requirement], Graph) -> Graph
        if not requirements:
            return graph

        # Extract the top level requirement
        req = requirements[0]
        req_key = _create_key(req)
        requirements = requirements[1:]

        if req_key in graph:
            # We have seen this requirement; check if we satisfy it already
            chosen_before = graph[req_key]
            if not chosen_before.matches(req):
                raise CannotSatisfy(req, chosen_before)
            # Proceed to the next requirement
            try:
                retval = self._resolve(requirements, graph)
            except CannotSatisfy:
                raise
            else:
                return retval

        candidates = self.provider.get_candidates(req)
        for candidate in candidates:
            assert candidate.matches(req), (
                "candidate does not match requirement it was guaranteed " "to match"
            )

            graph[req_key] = candidate
            deps = self.provider.get_dependencies(candidate)
            try:
                # XXX: This causes a peak in memory usage.
                retval = self._resolve(deps + requirements, graph.copy())
            except CannotSatisfy:
                assert graph[req_key] == candidate
                del graph[req_key]
            else:
                return retval

        # If we are here, we could not satisfy the given requirements
        raise CannotSatisfy([req] + requirements, graph)
