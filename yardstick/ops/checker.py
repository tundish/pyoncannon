#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of yardstick.
#
# yardstick is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# yardstick is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with yardstick.  If not, see <http://www.gnu.org/licenses/>.

import configparser
import logging
import platform
import unittest


shebang = """
#!/usr/bin/env python3
# encoding: UTF-8

""".lstrip()

imports = [
    "ast", "collections", "collections.abc", "csv", "configparser", "ctypes",
    "datetime", "difflib", "errno", "filecmp", "functools", "glob", "grp",
    "gzip", "hashlib", "html", "inspect", "io", "ipaddress", "itertools",
    "json", "linecache", "locale", "logging", "os", "pathlib", "platform",
    "posix", "random", "re", "resource", "shlex", "shutil", "signal", "site",
    "string", "struct", "stat", "subprocess", "sys", "sysconfig", "syslog",
    "tarfile", "tempfile", "time", "timeit", "types", "textwrap",
    "unicodedata", "uuid", "unittest", "venv", "warnings", "xml", "zipfile",
    "zlib" 
]


def check(class_):
    """
    Executed on the target by the `check` command.

    :param class_: A class of tests.
    :type class_: unittest.TestCase
    :requires: `platform`, `unittest`.
    """
    logName="yardstick.{}".format(class_.__name__)
    try:
        msg = log_message(
            logging.INFO,
            msg="Executing from {}.".format(platform.node()),
            name=logName)
        channel.send(msg)

        config = channel.receive()
        try:
            class_.ini = config_parser()
            class_.ini.read_string(config)
            class_.settings = config_settings(class_.ini)
        except Exception as e:
            class_.ini = None
            class_.settings = {}
            channel.send(config)
            channel.send(str(getattr(e, "args", e) or e))

        class_.args = channel.receive()
        class_.sudoPwd = channel.receive()
        class_.ts = channel.receive()

        ldr = unittest.defaultTestLoader
        suite = ldr.loadTestsFromTestCase(class_)
        runner = unittest.TextTestRunner(
            resultclass=unittest.TestResult,
            failfast=class_.args.get("failfast", False),
        )
        rlt = runner.run(suite)

        msg = log_message(logging.INFO, msg="Check complete.", name=logName)
        channel.send(msg)

        rv = {a: [i[1] for i in getattr(rlt, a)]
                for a in ("errors", "failures", "skipped")}
        rv["total"] = rlt.testsRun
        channel.send(rv)
    except (EOFError, OSError) as e:
        channel.send(str(getattr(e, "args", e) or e))
    except Exception as e:
        channel.send(str(getattr(e, "args", e) or e))
    finally:
        channel.send(None)
