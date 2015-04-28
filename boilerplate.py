#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of yardstick.
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
# along with yardstick.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import logging.handlers
import os.path
import platform
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

Help for each option is printed on the command::

    boilerplate.py --help

Don't forget you can supply command line-options from a file as described
here:

https://docs.python.org/3/library/argparse.html#fromfile-prefix-chars

This gives a way of 'baking in' certain options to suit particular environments
or configurations of the system.

eg::

    cloudhands-orgadmin \\
    --host=jasmin-cloud.jc.rl.ac.uk --identity=~/.ssh/id_rsa-jasminvm \\
    --db=/home/jasminuser/jasmin-web.sl3 \\
    --account=denderby \\
    --email=dominic.enderby@contractor.net \\
    --surname=enderby \\
    --organisation=STFCloud \\
    --public=172.16.151.170/30 \\
    --activator=/root/bootstrap.sh \\
    --providers=cloudhands.jasmin.vcloud.phase04.cfg

"""

DFLT_PORT = 22
DFLT_DB = ":memory:"
DFLT_USER = "devops"
DFLT_VENV = "devops-py3.4"


def main(args):
    log = logging.getLogger("yardstick")

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

    s = ("ssh=-i {identity} -p {0.port} {0.user}@{0.host}"
         "//python=/home/{0.user}/{0.venv}/bin/python").format(
        args, identity=os.path.expanduser(args.identity))
    gw = execnet.makegateway(s)
    try:
        ch = gw.remote_exec(sys.modules[__name__])
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
        "--host", required=True,
        help="Specify the name of the remote host")
    rv.add_argument(
        "--port", type=int, default=DFLT_PORT,
        help="Set the port number [{}] to the host".format(DFLT_PORT))
    rv.add_argument(
        "--user", default=DFLT_USER,
        help="Specify the user login [{}] on the host".format(DFLT_USER))
    rv.add_argument(
        "--venv", default=DFLT_VENV,
        help="Specify the Python environment [{}] on the remote host".format(
            DFLT_VENV)
        )
    rv.add_argument(
        "--db", default=DFLT_DB,
        help="Set the path to the database [{}]".format(DFLT_DB))
    rv.add_argument(
        "--identity", default="",
        help="Specify the path to a SSH public key file authorised on the host")

    # Extra arguments here

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
