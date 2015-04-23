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

This module contains boilerplate for devops utilities.

It's your starting point for command-line tools which invoke Python functions
on remote hosts.

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
    host = args.host or ipaddress.ip_interface(settings["admin.net"])
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

def main(args, name="yardstick"):
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

    rv = 0
    s = execnet_string(ini, args)
    if s.startswith("popen"):
        log.warning("Local invocation.")

    gw = execnet.makegateway()
    try:
        ch = gw.remote_exec(sys.modules[__name__]) # Collect fragments with inspect
        ch.send(config)
        ch.send({k: v for k, v in vars(args).items() if not isinstance(v, list)})
        ch.send(sudoPwd)

        msg = ch.receive()
        while msg is not None:
            log.info(msg)
            msg = ch.receive()

    except (EOFError, OSError) as e:
        log.error(s)
        rv = 1
    except (Error, Exception) as e:
        log.error(getattr(e, "args", e) or e)
        rv = 1
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
        help="Specify the path to a SSH private key file [{}]".format(
            DFLT_IDENTITY
        ))
    rv.add_argument(
        "-f", "--forget", action="store_true", default=False,
        help="remove hosts from file {}".format(KNOWN_HOSTS))
    rv.add_argument(
        "--version", action="store_true", default=False,
        help="Print the current version number")
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
