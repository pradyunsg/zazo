"""
"""
from __future__ import absolute_import

import abc

from six import add_metaclass

if False:
    from packaging.requirements import Requirement  # NOQA
    from packaging.version import Version  # NOQA
    from typing import List  # NOQA


@add_metaclass(abc.ABCMeta)
class Candidate(object):

    @abc.abstractmethod
    def matches(self, requirement):
        # type: (Requirement) -> bool
        raise NotImplementedError("Method to be overridden in a subclass.")


@add_metaclass(abc.ABCMeta)
class Provider(object):
    """Handles everything related to providing packages and package information
    """

    @abc.abstractmethod
    def get_candidates(self, requirement):
        # type: (Requirement) -> List[Candidate]
        raise NotImplementedError("Method to be overridden in a subclass.")

    @abc.abstractmethod
    def fetch_dependencies(self, candidate):
        # type: (Candidate) -> List[Requirement]
        raise NotImplementedError("Method to be overridden in a subclass.")
