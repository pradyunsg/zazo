"""
"""


class ZazoError(Exception):
    """Base of all exceptions
    """


class CannotSatisfy(ZazoError):
    """A requested candidate cannot be satisfied
    """
