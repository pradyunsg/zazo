import nox

LINT_FILES = "docs", "src", "tests", "nox.py"


@nox.session
def docs(session):
    session.install("-r", "tools/reqs/docs.txt")

    session.run("sphinx-build", "-W", "-n", "-b", "html", "docs/source", "docs/build")


@nox.session
def format(session):
    session.install("-r", "tools/reqs/lint.txt")

    session.run("black", *LINT_FILES)
    session.run("isort", "--recursive", *LINT_FILES)


@nox.session
def lint(session):
    session.install("-r", "tools/reqs/lint.txt")
    session.install("-e", ".")

    session.run("black", "--diff", "--check", *LINT_FILES)
    session.run("isort", "--diff", "--check-only", "--recursive", *LINT_FILES)
    session.run("mypy", "--strict", "--ignore-missing-imports", "src")
    session.run("mypy", "--strict", "--ignore-missing-imports", "-2", "src")


@nox.session
def packaging(session):
    session.install("check-manifest")

    session.run("check-manifest")
    session.run("python", "setup.py", "check", "-m", "-s")


@nox.session(python=["2.7", "3.4", "3.5", "3.6", "3.7", "3.8", "pypy", "pypy3"])
def test(session):
    session.install("-r", "tools/reqs/test.txt")
    session.install("-e", ".")
    session.run("pytest")
