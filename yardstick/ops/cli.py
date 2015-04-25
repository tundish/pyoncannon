#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of pyoncannon.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyoncannon.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import os
import sys


__doc__ = """

The yardstick program supports system administration of remote nodes.

It lets you select and launch:

* tests written in Python
* modification tasks controlled by a `.ini` file

"""

import yardstick.ops.base


def parsers(description=__doc__):
    parser = argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    parser.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    parser.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    parser.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")

    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands:",
    )
    return (parser, subparsers)


def add_common_options(parser):
    parser.add_argument(
        "--ini", nargs="*",
        type=argparse.FileType('r'), default=[sys.stdin],
        help="Specify one or more .ini files to process "
        "(or else read stdin).")
    parser.add_argument(
        "--modules", nargs="*",
        default=[],
        help="Specify one or more Python modules to process.")
    parser.add_argument(
        "--paths", nargs="*",
        default=[],
        help="Specify one or more file paths to process.")
    parser.add_argument(
        "--show", action="store_true", default=False,
        help="Print the code for each task, but do not execute it")
    return parser


def add_auto_command_parser(subparsers):
    rv = subparsers.add_parser(
        "auto", help="Run tasks which modify the target.",
        description="", epilog="other commands: check, units"
    )
    rv.add_argument(
        "--host", required=False,
        help="Specify the name of the remote host")
    rv.add_argument(
        "--port", type=int, required=False,
        help="Specify the port number to the host")
    rv.add_argument(
        "--user", required=False,
        help="Specify the user login on the host")
    rv.add_argument(
        "--python", required=False,
        help="Specify the Python executable on the remote host")
    rv.add_argument(
        "--identity", default=yardstick.ops.base.DFLT_IDENTITY,
        help="Specify the path to a local SSH private key file ['{}']".format(
            yardstick.ops.base.DFLT_IDENTITY
        ))
    rv.add_argument(
        "--forget", action="store_true", default=False,
        help="Remove existing host key from the file '{}'".format(
            yardstick.ops.base.KNOWN_HOSTS
        ))
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    rv = add_common_options(rv)
    rv.usage = rv.format_usage().replace("usage:", "").replace(
        "auto", "\n\nyardstick [OPTIONS] auto")
    return rv
 
def add_check_command_parser(subparsers):
    rv = subparsers.add_parser(
        "check", help="Run tests which don't modify the target.",
        description="", epilog="other commands: auto, units"
    )
    rv.add_argument(
        "--host", required=False,
        help="Specify the name of the remote host")
    rv.add_argument(
        "--port", type=int, required=False,
        help="Specify the port number to the host")
    rv.add_argument(
        "--user", required=False,
        help="Specify the user login on the host")
    rv.add_argument(
        "--python", required=False,
        help="Specify the Python executable on the remote host")
    rv.add_argument(
        "--identity", default=yardstick.ops.base.DFLT_IDENTITY,
        help="Specify the path to a local SSH private key file ['{}']".format(
            yardstick.ops.base.DFLT_IDENTITY
        ))
    rv.add_argument(
        "--forget", action="store_true", default=False,
        help="Remove existing host key from the file '{}'".format(
            yardstick.ops.base.KNOWN_HOSTS
        ))
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    rv.add_argument(
        "--failfast", action="store_true", default=False,
        help="Halt checks on the first failure")
    rv = add_common_options(rv)
    rv.usage = rv.format_usage().replace("usage:", "").replace(
        "check", "\n\nyardstick [OPTIONS] check")
    return rv
 
def add_units_command_parser(subparsers):
    rv = subparsers.add_parser(
        "units", help="Find and filter tests by their attributes.",
        description="", epilog="other commands: auto, check"
    )
    rv.usage = rv.format_usage().replace("usage:", "").replace(
        "units", "\n\nyardstick [OPTIONS] units")
    return rv
