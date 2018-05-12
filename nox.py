import functools

import nox

LINT_ITEMS = "nox.py", "docs/source/conf.py", "zazo", "tests"


@nox.session
def docs(session):
    session.interpreter = "python3.6"
    session.install("-r", "tools/reqs/docs.txt")

    session.run("sphinx-build", "-n", "-b", "html", "docs/source", "docs/build")


@nox.session
def packaging(session):
    session.interpreter = "python3.6"
    session.install("-r", "tools/reqs/packaging.txt")

    session.run("flit", "build")


def lint_session(func):

    @functools.wraps(func)
    def wrapped(session):
        if session.posargs:
            files = session.posargs
        else:
            files = LINT_ITEMS
        session.install("-r", "tools/reqs/lint.txt")

        return func(session, files)

    return wrapped


@nox.session
@lint_session
def lint(session, files):
    session.run("black", "--check", *files)
    session.run("isort", "--check-only", "--diff", "--recursive", *files)
    session.run("mypy", "--ignore-missing-imports", "--check-untyped-defs", *files)
    session.run(
        "mypy", "-2", "--ignore-missing-imports", "--check-untyped-defs", *files
    )


@nox.session
@lint_session
def lint_format(session, files):
    session.run("black", *files)
    session.run("isort", "--recursive", *files)


@nox.session
@nox.parametrize("python_version", ["2.7", "3.4", "3.5", "3.6", "3.7", "pypy", "pypy3"])
def test(session, python_version):
    if python_version.startswith("pypy"):
        session.interpreter = python_version
    else:
        session.interpreter = "python" + python_version

    session.install("-r", "tools/reqs/test.txt")

    session.run("pytest", *session.posargs)
