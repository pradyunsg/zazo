import os
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    try:
        with open(os.path.join(here, *parts), 'r') as f:
            return f.read()
    except IOError:
        return "Could not read."


def find_version(*file_paths):
    regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_file = read(*file_paths)
    version_match = re.search(regex, version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Keep README.md ASCII-only
long_description = read('README.md')

setup(
    name="zazo",
    version=find_version("src", "zazo", "__init__.py"),
    url="http://zazo.readthedocs.io",
    description="An Extensible Dependency Resolver written in Python",
    long_description=long_description,

    license="MIT",
    keywords=["zazo", "pip", "dependency resolution"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy"
    ],
    author='Pradyun S. Gedam',
    author_email='pradyunsg@gmail.com',

    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["docs", "tests"]),
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',
    install_requires=['packaging', 'six'],
    zip_safe=True,
)
