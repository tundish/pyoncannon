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

__doc__ = """
Entry point for the yardstick program.

"""

from getpass import getpass
import logging
import sys

import yardstick
import yardstick.ops.base
import yardstick.ops.cli


def run():
    p, subs = yardstick.ops.cli.parsers()
    yardstick.ops.cli.add_auto_command_parser(subs)
    yardstick.ops.cli.add_check_command_parser(subs)
    yardstick.ops.cli.add_units_command_parser(subs)
    args = p.parse_args()

    rv = 0
    if args.version:
        sys.stdout.write(yardstick.__version__ + "\n")
    else:
        if args.command in ("auto", "units"):
            raise NotImplementedError("This feature is not yet available.")

        logName = yardstick.ops.base.log_setup(
            args, "yardstick.{}".format(args.command)
        )
        log = logging.getLogger(logName)

        if sys.stdin in args.ini:
            log.info("Accepting stream input.")

        config = '\n'.join(i.read() for i in args.ini)
        ini = yardstick.ops.modder.config_parser()
        ini.read_string(config)

        if ini.sections():
            sudoPwd = getpass(
                "Enter sudo password for {}:".format(settings["admin.user"]))
        else:
            sudoPwd = None

        for text in yardstick.ops.base.gen_check_tasks(args):
            if args.show:
                print(text)
            else:
                rv = yardstick.ops.base.operate(
                    text, config, args, sudoPwd, logName
                )
                print("\n")
                print(
                    *[i for a in ("skipped", "failures", "errors")
                        for i in rv[a]],
                    sep="\n"
                )
                print("Total: {}".format(rv["total"]))

    sys.exit(1 if rv is None else 0)

if __name__ == "__main__":
    run()
