#!/bin/bash
set -e
set -x

git config --global user.name "Travis CI"
git config --global user.email "$COMMIT_AUTHOR_EMAIL"

pip install --upgrade setuptools
pip install --upgrade tox
