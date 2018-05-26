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


@nox.session
@nox.parametrize("python_version", ["2.7", "3.4", "3.5", "3.6", "3.7", "pypy", "pypy3"])
def test(session, python_version):
    # Set the interpreter
    if python_version.startswith("pypy"):
        session.interpreter = python_version
    else:
        session.interpreter = "python" + python_version

    # Build the package.
    # THIS IS A HACK
    #   Working around all kinds of weird nox + flit + Travis CI behavior.
    #   We're building a wheel here and installing it with session.install since
    #   nox is declarative but we need to run the build command before executing
    #   code.
    def my_run(*args):
        print("run > " + " ".join(args))
        try:
            subprocess.check_call(args)
        except subprocess.CalledProcessError:
            session.error("Command failed.")

    my_run("python3", "-m", "flit", "build")
    files = glob.glob("./dist/*.whl")
    if not files:
        session.error("Could not find any built wheels.")

    # Install the package and test dependencies.
    session.install(*files)
    session.install("-r", "tools/reqs/test.txt")

    # Run the tests
    session.cd("tests")  # we change directory to avoid the cwd ambiguity
    session.run("pytest", *session.posargs)
