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

import inspect
import logging
import platform
import subprocess
import sys
import textwrap
import unittest

try:
    from yardstick import __version__
except ImportError:
    # Remote host
    __version__ = None

if __name__ == "__main__":
    import yardstick.cli
    import yardstick.composition

    p, subs = yardstick.cli.parsers()
    yardstick.cli.add_auto_command_parser(subs)
    yardstick.cli.add_check_command_parser(subs)
    yardstick.cli.add_units_command_parser(subs)
    args = p.parse_args()

    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        ldr = unittest.defaultTestLoader
        # specific to check command
        logName = yardstick.cli.log_setup(args, "yardstick.check")
        testClasses = {
            type(meth) for mod in ldr.discover("yardstick.openrc")
            for suite in mod for meth in suite
        }

        for class_ in testClasses:
            checkLines, nr = inspect.getsourcelines(
                yardstick.composition.check
            )
            checkLines[0] = 'if __name__ == "__channelexec__":\n'
            text = "\n".join((
                "\n".join("import {}".format(i)
                          for i in yardstick.composition.imports),
                "",
                inspect.getsource(class_),
                inspect.getsource(yardstick.cli.config_parser),
                "".join(checkLines).replace("class_", class_.__name__)
            ))
            print(text)
            rv = yardstick.cli.main(text, args, logName)
            print("\n")
            print(
                *[i for a in ("skipped", "failures", "errors")
                    for i in rv[a]],
                sep="\n"
            )
            print("Total: {}".format(rv["total"]))

    sys.exit(1 if rv is None else 0)
