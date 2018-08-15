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
    session.run("mypy", "--ignore-missing-imports", "--check-untyped-defs", "zazo")
    session.run(
        "mypy", "-2", "--ignore-missing-imports", "--check-untyped-defs", "zazo"
    )


@nox.session
@lint_session
def format(session, files):
    session.run("black", *files)
    session.run("isort", "--recursive", *files)


@nox.session(python=["2.7", "3.4", "3.5", "3.6", "3.7", "pypy", "pypy3"])
def test(session):
    session.install("flit")
    session.run("python3", "-m", "flit", "build")

    files = glob.glob("./dist/*.whl")
    if not files:
        session.error("Could not find any built wheels.")

    # Install the package and test dependencies.
    session.install(*files)
    session.install("-r", "tools/reqs/test.txt")

    # Run the tests
    session.cd("tests")  # we change directory to avoid the cwd ambiguity
    session.run("pytest", *session.posargs)
