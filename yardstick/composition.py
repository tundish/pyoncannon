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

shebang = """
#!/usr/bin/env python3
# encoding: UTF-8

""".lstrip()

imports = [
    "ast", "collections", "csv", "configparser", "ctypes", "datetime",
    "difflib", "errno", "filecmp", "glob", "grp", "gzip", "hashlib",
    "html", "inspect", "io", "ipaddress", "json", "locale", "linecache", "os",
    "pathlib", "platform", "posix", "random", "re", "resource", "shlex",
    "shutil", "signal", "site", "string", "struct", "stat", "subprocess",
    "sys", "sysconfig", "syslog", "tarfile", "tempfile", "time", "timeit",
    "types", "textwrap", "unicodedata", "uuid", "unittest", "venv",
    "warnings", "xml", "zipfile", "zlib" 
]


def check(class_):
    """
    Executed on the target by the `check` command.

    :param class_: A class of tests.
    :type class_: unittest.TestCase
    :requires: `platform`, `unittest`, `yardstick.cli.config_parser`.
    """
    try:
        channel.send("Executing from {}.".format(platform.node()))
        class_.ini = channel.receive()
        class_.args = channel.receive()
        class_.sudoPwd = channel.receive()
        # TODO: config_parser on .ini
        ldr = unittest.defaultTestLoader
        suite = ldr.loadTestsFromTestCase(class_)
        # TODO: failfast
        runner = unittest.TextTestRunner(resultclass=unittest.TestResult)
        rlt = runner.run(suite)
        rv = {a: [i[1] for i in getattr(rlt, a)]
                for a in ("errors", "failures", "skipped")}
        rv["total"] = rlt.testsRun
        channel.send(rv)
    except (EOFError, OSError) as e:
        channel.send(str(getattr(e, "args", e) or e))
    except (Error, Exception) as e:
        channel.send(str(getattr(e, "args", e) or e))
    finally:
        channel.send(None)


