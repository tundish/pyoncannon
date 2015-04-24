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
import configparser
from getpass import getpass
import ipaddress
import logging
import logging.handlers
import os
import os.path
import subprocess
import sys

try:
    from yardstick import __version__
    import execnet
except ImportError:
    # Remote host
    __version__ = None

__doc__ = """

The yardstick program supports system administration of remote nodes.

It lets you select and launch:

* tests written in Python
* modification tasks controlled by a `.ini` file

"""

DFLT_IDENTITY = os.path.expanduser(os.path.join("~", ".ssh", "id_rsa"))
DFLT_PORT = 22
DFLT_USER = "root"
KNOWN_HOSTS = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))


def forget_host(host):
    subprocess.check_call(["ssh-keygen", "-f", KNOWN_HOSTS, "-R", host])

def config_parser():
    return configparser.ConfigParser(
        strict=True,
        empty_lines_in_values=True,
        allow_no_value=True,
        interpolation=configparser.ExtendedInterpolation()
    )

def config_settings(ini):
    # TODO: check defaults section
    return ini.defaults()

def execnet_string(ini, args):
    settings = config_settings(ini)
    port = args.port or settings["admin.port"] or DFLT_PORT
    user = args.user or settings["admin.user"] or DFLT_USER
    host = args.host or ipaddress.ip_interface(settings["admin.net"]).ip
    python = args.python or settings["admin.python"] or sys.executable

    #"//python=/home/{user}/{0.venv}/bin/python").format(
    if host in (None, "0.0.0.0", "127.0.0.1", "localhost"):
        rv = "popen//dont_write_bytecode"
    else:
        rv = ("ssh=-i {identity} -p {port} {user}@{host}"
         "//python={python}").format(
            identity=os.path.expanduser(args.identity),
            host=host, port=port, user=user, python=python
        )
    return rv

def log_setup(args, name="yardstick"):
    log = logging.getLogger(name)

    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = logging.handlers.WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)
    return name

def main(module, args, name="yardstick"):
    log = logging.getLogger(name)

    if sys.stdin in args.ini:
        log.info("Accepting stream input.")

    ini = config_parser()
    config = '\n'.join(i.read() for i in args.ini)
    ini.read_string(config)
    settings = config_settings(ini)

    if ini.sections():
        sudoPwd = getpass(
            "Enter sudo password for {}:".format(settings["admin.user"]))
    else:
        sudoPwd = None

    if args.forget:
        host = ipaddress.ip_interface(settings["admin.net"])
        forget_host(host.ip.compressed)
        forget_host(host.ip.exploded)

    rv = None
    s = execnet_string(ini, args)
    log.debug(s)
    if s.startswith("popen"):
        log.warning("Local invocation.")

    if args.debug:
        os.environ["EXECNET_DEBUG"] = "2"

    gw = execnet.makegateway(s)
    try:
        ch = gw.remote_exec(module)
        ch.send(config)
        ch.send({k: v for k, v in vars(args).items() if not isinstance(v, list)})
        ch.send(sudoPwd)

        msg = ch.receive()
        while msg is not None:
            log.debug(msg) # TODO: msg types, levels
            prev, msg = msg, ch.receive()
        else:
            rv = prev

    except (EOFError, OSError) as e:
        log.error(s)
    except (Error, Exception) as e:
        log.error(getattr(e, "args", e) or e)
    finally:
        gw.exit()

    return rv

def parser(description=__doc__):
    rv = argparse.ArgumentParser(
        description,
        fromfile_prefix_chars="@"
    )
    rv.add_argument(
        "--host", required=False,
        help="Specify the name of the remote host")
    rv.add_argument(
        "--port", type=int, required=False,
        help="Set the port number to the host")
    rv.add_argument(
        "--user", required=False,
        help="Specify the user login on the host")
    rv.add_argument(
        "--python", required=False,
        help="Specify the Python executable on the remote host")
    rv.add_argument(
        "--identity", default=DFLT_IDENTITY,
        help="Specify the path to a local SSH private key file ['{}']".format(
            DFLT_IDENTITY
        ))
    rv.add_argument(
        "--forget", action="store_true", default=False,
        help="Remove hosts from the file '{}'".format(KNOWN_HOSTS))
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    rv.add_argument(
        "-v", "--verbose", required=False,
        action="store_const", dest="log_level",
        const=logging.DEBUG, default=logging.INFO,
        help="Increase the verbosity of output")
    rv.add_argument(
        "--log", default=None, dest="log_path",
        help="Set a file path for log output")
    rv.add_argument(
        "ini", nargs="*",
        type=argparse.FileType('r'), default=[sys.stdin],
        help="Specify one or more .ini files to process "
        "(or else read stdin).")
    return rv

# TODO: add test package option
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

    subparsers = parser.add_subparsers(
        dest="command",
        help="Commands:",
    )
    return (parser, subparsers)


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
        "--identity", default=DFLT_IDENTITY,
        help="Specify the path to a local SSH private key file ['{}']".format(
            DFLT_IDENTITY
        ))
    rv.add_argument(
        "--forget", action="store_true", default=False,
        help="Remove existing host key from the file '{}'".format(
            KNOWN_HOSTS
        ))
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
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
        "--identity", default=DFLT_IDENTITY,
        help="Specify the path to a local SSH private key file ['{}']".format(
            DFLT_IDENTITY
        ))
    rv.add_argument(
        "--forget", action="store_true", default=False,
        help="Remove existing host key from the file '{}'".format(
            KNOWN_HOSTS
        ))
    rv.add_argument(
        "--debug", action="store_true", default=False,
        help="Print wire-level messages for debugging")
    # TODO: add failfast
    # TODO: add printing of module.
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
 
