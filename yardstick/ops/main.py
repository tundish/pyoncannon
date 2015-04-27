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


def main(args):
    if args.command is None:
        return 2

    logName = yardstick.ops.base.log_setup(
        args, "yardstick.{}".format(args.command)
    )
    log = logging.getLogger(logName)

    if sys.stdin in args.ini:
        log.info("Accepting stream input.")

    config = '\n'.join(i.read() for i in args.ini)
    ini = yardstick.ops.modder.config_parser()
    ini.read_string(config)
    settings = yardstick.ops.modder.config_settings(ini)

    if any(
        ini.getboolean(sec, "sudo", fallback=False)
        for sec in ini.sections()
    ):
        sudoPwd = getpass(
            "Enter sudo password for {}:".format(settings["admin.user"]))
    else:
        sudoPwd = None

    if args.show:
        ini.write(sys.stdout)
        sys.stdout.write("\n")

    rv = 0
    if args.command == "auto":
        for code in yardstick.ops.base.gen_auto_tasks(args):
            if args.show:
                print(code)
            else:
                rv = yardstick.ops.base.operate(
                    code, config, args, sudoPwd, logName
                )

    elif args.command == "check":

        for code in yardstick.ops.base.gen_check_tasks(args):
            if args.show:
                print(code)
            else:
                rv = yardstick.ops.base.operate(
                    code, config, args, sudoPwd, logName
                )

            if rv is not None:
                print("\n")
                print(
                    *[i for a in ("skipped", "failures", "errors")
                        for i in rv[a]],
                    sep="\n"
                )
                print("Total: {}".format(rv["total"]))

    elif args.command == "units":
        raise NotImplementedError("This feature is not yet available.")

    return rv


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
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
