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
    parts = [req.name]

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
            retval = self._resolve(requirements, graph, _log=logger.debug)
        except CannotSatisfy:
            logger.debug("Unable to satisfy dependencies.")
            raise
        else:
            logger.debug("Found satisfying set: %s", retval)
            return retval

    # TODO: Figure out feasibility of blacklisting of known conflicts, like
    #       Stork.
    def _resolve(self, requirements, graph, _log):
        # type: (List[Requirement], Graph, Any) -> Graph
        if not requirements:
            return graph

        # Extract the top level requirement
        req = requirements[0]
        req_key = _create_key(req)
        requirements = requirements[1:]

        s = ""  # noqa
        # The following is some stuff for logging clarity (comment when unused)
        recursion_depth = len(inspect.stack()) - self._initial_recursion_depth
        s += "  " * (recursion_depth - 1)  # noqa

        _log(s + "will attempt to satisfy: %s", req)
        if req_key in graph:
            # We have seen this requirement; check if we satisfy it already
            chosen_before = graph[req_key]
            _log(s + "  already chosen: %s", chosen_before)
            if not chosen_before.matches(req):
                _log(s + "    does not match requirement")
                raise CannotSatisfy(req, chosen_before)
            _log(s + "    does match requirement")
            # Proceed to the next requirement
            try:
                retval = self._resolve(requirements, graph, _log)
            except CannotSatisfy:
                raise
            else:
                _log(s + "proceeding with existing choice: %s", chosen_before)
                return retval

        _log(s + "  not chosen yet: %s", req_key)
        candidates = self.provider.get_candidates(req)
        for candidate in candidates:
            assert candidate.matches(req), (
                "candidate does not match requirement it was guaranteed "
                "to match"
            )
            _log(s + "  choosing: %s", candidate)

            graph[req_key] = candidate
            deps = self.provider.fetch_dependencies(candidate)
            try:
                # XXX: This causes a peak in memory usage.
                retval = self._resolve(deps + requirements, graph, _log)
            except CannotSatisfy:
                assert graph[req_key] == candidate
                del graph[req_key]
            else:
                _log(s + "proceeding with choice: %s", candidate)
                return retval

        # If we are here, we could not satisfy the given requirements
        raise CannotSatisfy([req] + requirements, graph)
