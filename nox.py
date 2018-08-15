import functools
import glob
import subprocess

import nox

LINT_ITEMS = "nox.py", "docs/source/conf.py", "zazo", "tests"


@nox.session
def docs(session):
    session.install("-r", "tools/reqs/docs.txt")

    session.run("sphinx-build", "-n", "-b", "html", "docs/source", "docs/build")


@nox.session
def packaging(session):
    session.install("-r", "tools/reqs/packaging.txt")

    session.run("flit", "build")


def lint_session(func):
    @functools.wraps(func)
    def wrapped(session):
        if session.posargs:
            files = session.posargs
        else:
            files = LINT_ITEMS
        session.install("--pre", "-r", "tools/reqs/lint.txt")

        # We'll install our actual dependencies for installation here; instead of
        # depending on flit or pip to install (because we can't)
        session.install("flit")
        session.run("flit", "install")

        session.run("black", "--version")
        session.run("isort", "--version")
        session.run("mypy", "--version")

        return func(session, files)

    return wrapped


@nox.session
@lint_session
def lint(session, files):
    session.run("black", "--check", "--diff", *files)
    session.run("isort", "--check-only", "--diff", "--recursive", *files)
    # NOTE: Added ignore-missing-imports here since packaging doesn't have type
    #       annotations. Would be a good thing to do, since that'd allow to be
    #       strict here.
    session.run("mypy", "--strict", "--ignore-missing-imports", "zazo")
    session.run("mypy", "--strict", "--ignore-missing-imports", "-2", "zazo")


@nox.session
@lint_session
def format(session, files):
    session.run("black", *files)
    session.run("isort", "--recursive", *files)


@nox.session(python=["2.7", "3.4", "3.5", "3.6", "3.7", "3.8", "pypy", "pypy3"])
def test(session):
    session.install("flit")
    session.run("flit", "install")

    session.install("-r", "tools/reqs/test.txt")

    # Run the tests
    session.cd("tests")  # we change directory to avoid the cwd ambiguity
    session.run("pytest", *session.posargs)
