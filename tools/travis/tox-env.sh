#!/bin/bash
set -x
set -e

echo "Determining correct TOXENV..."
if [[ -z "$TOXENV" || -z "$SESSION" ]]; then
    if [[ ${TRAVIS_PYTHON_VERSION} == pypy* ]]; then
        export TOXENV=${TRAVIS_PYTHON_VERSION}
    else
        # We use the syntax ${string:index:length} to make 2.7 -> py27
        _major=${TRAVIS_PYTHON_VERSION:0:1}
        _minor=${TRAVIS_PYTHON_VERSION:2:1}
        export TOXENV="py${_major}${_minor}"
    fi
fi
echo "TOXENV=${TOXENV}"

set +x
set +e
