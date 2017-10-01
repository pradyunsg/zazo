#!/bin/bash
set -e
set -x

git config --global user.name "Travis CI"
git config --global user.email "travis@travis-ci.org"

pip install --upgrade setuptools
pip install --upgrade tox
