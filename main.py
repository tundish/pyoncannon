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
Checks the remote access configuration on a node.

::

    main.py < demo/manjaro_openrc_net-virtualbox.ini
"""

import sys

import yardstick
import yardstick.base
import yardstick.cli


if __name__ == "__main__":
    p, subs = yardstick.cli.parsers()
    yardstick.cli.add_auto_command_parser(subs)
    yardstick.cli.add_check_command_parser(subs)
    yardstick.cli.add_units_command_parser(subs)
    args = p.parse_args()

    if args.version:
        sys.stdout.write(yardstick.__version__ + "\n")
        rv = 0
    else:
        # specific to check command
        logName = yardstick.base.log_setup(args, "yardstick.check")
        for text in yardstick.base.check_tasks(args):
            rv = yardstick.base.operate(text, args, logName)
            print("\n")
            print(
                *[i for a in ("skipped", "failures", "errors")
                    for i in rv[a]],
                sep="\n"
            )
            print("Total: {}".format(rv["total"]))

    sys.exit(1 if rv is None else 0)
