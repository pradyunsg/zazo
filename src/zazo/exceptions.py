"""
"""


class ZazoError(Exception):
    """Base of all exceptions
    """


class CannotSatisfy(ZazoError):
    """A requested candidate cannot be satisfied
    """


class GraphError(ZazoError):
    """Base of all Graph related exceptions
    """


class DuplicateVertexError(GraphError):
    """A vertex cannot be duplicated
    """


class NonExistentVertexError(ZazoError):
    """A vertex does not exist in class
    """
