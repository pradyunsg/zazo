# zazo

[![Build Status](https://travis-ci.org/pradyunsg/zazo.svg?branch=master)](https://travis-ci.org/pradyunsg/zazo)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)

An extensible Dependency Resolver, written in Python. Intended for bringing dependency resolution to pip.

## Motivation

The motivation for this project is to make it feasible and easy for user-facing package managers written in Python to do proper dependency resolution.

This project has grown out of a [GSoC Project], which aimed to bring proper dependency resolution to pip. Once this package is ready, work will be done to make pip use this instead of its home-grown solution.

## Development

This project uses nox extensively.

- Documentation is built with `nox -s docs`.
- Linting and MyPy checking can be done using `nox -s lint`
- Tests are run with `nox -s test`.

Currently, the documentation of this project is non-existent but this shall be rectified once the actual internal details of the package stabilize.

[GSoC Project]: https://summerofcode.withgoogle.com/archive/2017/projects/5797394100781056/
