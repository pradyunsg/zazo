# zazo

[![Build Status](https://travis-ci.org/pradyunsg/zazo.svg?branch=master)](https://travis-ci.org/pradyunsg/zazo)

A Pluggable Dependency Resolver written in Python.

## Motivation

The motivation for this project is to make it feasible and easy for user-facing package managers written in Python to do proper dependency resolution.

This project has grown out of a [GSoC Project], which aimed to bring proper dependency resolution to pip. Once this package is ready, work will be done to make pip use this instead of its home-grown solution.

## Development

This project uses tox extensively.

- Documentation is built with `tox docs`.
- Tests are run with `tox py36`.
- Linting checks are done with `tox lint-py3` and `tox lint-py2`.
- MyPy checking can be done using `tox mypy`

Requirement Files containing dependencies for tests, documentation, linting etc are in `tools/reqs` folder.

Currently, the documentation of this project is lacking but this shall be rectified once the actual internal details of the package stabilize.

[GSoC Project]: https://summerofcode.withgoogle.com/archive/2017/projects/5797394100781056/
