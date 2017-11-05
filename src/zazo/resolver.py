"""
"""

import logging


from .exceptions import CannotSatisfy

if False:
    from typing import List, Dict  # NOQA
    from packaging.requirements import Requirement  # NOQA
    from .abc import Provider, Candidate  # NOQA

    Graph = Dict[str, Candidate]

logger = logging.getLogger()


class BacktrackingResolver(object):

    def __init__(self, provider):
        # type: (Provider) -> None
        super(BacktrackingResolver, self).__init__()
        self.provider = provider

    def resolve(self, requirements):
        # type: (List[Requirement]) -> Graph
        graph = {}  # type: Graph
        try:
            retval = self._resolve(requirements, graph)
        except CannotSatisfy:
            logger.debug("Unable to satisfy dependencies.")
            raise
        else:
            logger.debug("Found satisfying set: %s.", retval)
            return retval

    def _resolve(self, requirements, graph):
        # type: (List[Requirement], Graph) -> Graph
        if not requirements:
            return graph
        req = requirements[0]
        requirements = requirements[1:]

        logger.debug("will attempt to satisfy: %s", req)
        if req.name in graph:
            # We have seen this requirement; check if we satisfy it already
            existing_candidate = graph[req.name]
            logger.debug("  already selected: %s", existing_candidate)
            if not existing_candidate.matches(req):
                logger.debug("    does not match requirement")
                raise CannotSatisfy(req, existing_candidate)
            else:
                logger.debug("    does match requirement")
                # Proceed to the next requirement
                return self._resolve(requirements, graph)
        else:
            logger.debug("  not selected yet: %s", req.name)
            candidates = self.provider.get_candidates(req)
            logger.debug("  candidate count: %d", len(candidates), req.name)
            for candidate in candidates:
                assert candidate.matches(req), (
                    "candidate does not match requirement it was guaranteed "
                    "to match"
                )
                logger.debug("  selecting: %s", candidate)

                graph[req.name] = candidate
                dependencies = self.provider.fetch_dependencies(candidate)
                try:
                    return self._resolve(
                        dependencies + requirements, graph.copy()
                    )
                except CannotSatisfy:
                    assert graph[req.name] == candidate
                    del graph[req.name]

            # If we are here, we could not satisfy the given requirements
            raise CannotSatisfy([req] + requirements, graph.copy())
