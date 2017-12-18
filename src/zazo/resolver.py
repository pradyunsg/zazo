"""
"""

import inspect
import logging

from .exceptions import CannotSatisfy

if False:
    from typing import List, Dict  # NOQA
    from packaging.requirements import Requirement  # NOQA
    from .abc import Provider, Candidate  # NOQA

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
        # type: (List[Requirement], Graph) -> Graph
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
            existing_candidate = graph[req_key]
            _log(s + "  already selected: %s", existing_candidate)
            if not existing_candidate.matches(req):
                _log(s + "    does not match requirement")
                raise CannotSatisfy(req, existing_candidate)
            _log(s + "    does match requirement")
            # Proceed to the next requirement
            try:
                retval = self._resolve(requirements, graph, _log)
            except CannotSatisfy:
                raise
            else:
                _log(
                    s + "proceeding with existing selection %s",
                    existing_candidate,
                )
                return retval

        _log(s + "  not selected yet: %s", req_key)
        candidates = self.provider.get_candidates(req)
        for candidate in candidates:
            assert candidate.matches(req), (
                "candidate does not match requirement it was guaranteed "
                "to match"
            )
            _log(s + "  selecting: %s", candidate)

            graph[req_key] = candidate
            dependencies = self.provider.fetch_dependencies(candidate)
            try:
                retval = self._resolve(
                    dependencies + requirements, graph, _log,
                )
            except CannotSatisfy:
                assert graph[req_key] == candidate
                del graph[req_key]
            else:
                _log(s + "proceeding with selection %s", candidate)
                return retval

        # If we are here, we could not satisfy the given requirements
        raise CannotSatisfy([req] + requirements, graph)
