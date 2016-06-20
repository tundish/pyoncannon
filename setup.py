#!/usr/bin/env python
# encoding: UTF-8

import ast
import os.path
import sys

from setuptools import setup

kwargs = {}

try:
    # For setup.py install
    from yardstick import __version__ as version
except ImportError:
    # For pip installations
    version = str(
        ast.literal_eval(
            open(os.path.join(
                os.path.dirname(__file__),
                "yardstick", "__init__.py"),
                'r').read().split("=")[-1].strip()
        )
    )

deps = [
    "execnet>=1.3.0",
]

__doc__ = open(os.path.join(os.path.dirname(__file__), "README.rst"),
               'r').read()

setup(
    name="yardstick",
    version=version,
    description="Python toolkit for remote admin.",
    author="D Haynes",
    author_email="tundifh@thuswise.org",
    url="https://github.com/tundish/pyoncannon",
    long_description=__doc__,
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    packages=[
        "yardstick",
        "yardstick.ops",
        "yardstick.ops.test",
        "yardstick.utils",
    ],
    package_data={
        "yardstick": [
            "doc/*.rst",
            "doc/_templates/*.css",
            "doc/html/*.html",
            "doc/html/*.js",
            "doc/html/_sources/*",
            "doc/html/_static/css/*",
            "doc/html/_static/font/*",
            "doc/html/_static/js/*",
            "doc/html/_static/*.css",
            "doc/html/_static/*.gif",
            "doc/html/_static/*.js",
            "doc/html/_static/*.png",
        ],
        "yardstick.ops.test": [
            "*.ini",
        ],
    },
    install_requires=deps,
    extras_require={
        "dev": [
            "pep8>=1.6.2",
        ],
        "docbuild": [
            "babel>=2.2.0",
            "sphinx-argparse>=0.1.15",
            "sphinxcontrib-seqdiag>=0.8.4",
            "sphinx_rtd_theme>=0.1.9"
        ],
    },
    tests_require=[
    ],
    entry_points={
        "console_scripts": [
            "yardstick = yardstick.ops.main:run",
        ],
    },
    zip_safe=False,
    **kwargs
)
