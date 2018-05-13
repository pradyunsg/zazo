#!/bin/bash
set -x
set -e

# Install pip on Python 3 if we're on Python 2 / PyPy
if [ "$TRAVIS_PYTHON_VERSION" == "2.7" ] || [ "$TRAVIS_PYTHON_VERSION" == "pypy" ]; then
  wget https://bootstrap.pypa.io/get-pip.py
  python3 get-pip.py --user
  rm get-pip.py
  EXTRA_ARGS=--user
fi

# Install flit
python3 -m pip install $EXTRA_ARGS flit
