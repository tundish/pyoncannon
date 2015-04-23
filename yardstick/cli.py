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
import logging.handlers
import os.path
import platform
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
KNOWN_HOSTS = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))


def forget_host(host):
    subprocess.check_call(["ssh-keygen", "-f", KNOWN_HOSTS, "-R", host])

def execnet_string(ini, args):
    return ""

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

    #if self.askPass:
    #    self.sudoPass = getpass(
    #        "Enter sudo password for {}:".format(user))
    #else:
    #    self.sudoPass = None

    #if not self.rememberHosts:
    #    forget_host(str(host))

    log.warning(args)
    s = ("ssh=-i {identity} -p {0.port} {0.user}@{0.host}"
         "//python=/home/{0.user}/{0.venv}/bin/python").format(
        args, identity=os.path.expanduser(args.identity))
    gw = execnet.makegateway(s)
    try:
        ch = gw.remote_exec(sys.modules[__name__]) # Collect fragments with inspect
        # send .ini as string
        ch.send(vars(args))

        msg = ch.receive()
        while msg is not None:
            log.info(msg)
            msg = ch.receive()

    except OSError as e:
        log.error(s)
        log.error(e)
    finally:
        gw.exit()
    return 0


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
        "--venv", required=False,
        help="Specify the Python environment on the remote host")
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
        type=argparse.FileType('r'), default=sys.stdin,
        help="Specify one or more .ini files to process "
        "(or else read stdin).")
    return rv


def run():
    p = parser()
    args = p.parse_args()
    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()

if __name__ == "__channelexec__":
    channel.send("Executing remotely from {}.".format(platform.node()))
    args = channel.receive()
    channel.send("Received args {}.".format(args))
    channel.send(None)
