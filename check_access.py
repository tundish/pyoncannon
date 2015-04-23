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

    check_access.py < demo/manjaro_openrc_net-virtualbox.ini
"""

import inspect
import logging
import textwrap
import platform
import subprocess
import sys
import unittest

try:
    from yardstick import __version__
except ImportError:
    # Remote host
    __version__ = None

        
class OpenSSHChecks(unittest.TestCase):
    """
    https://help.ubuntu.com/community/SSH/OpenSSH/Configuring
    """
    def test_initial_config_copied_to_ref(self):
        st = os.stat("/etc/ssh/sshd_config")
        self.assertTrue(os.path.isfile("/etc/ssh/sshd_config.ref"))

    def test_sshd_on_defined_port(self):
        cfg = open("/etc/ssh/sshd_config").read()
        port = self.defn["sshd.port"]
        self.assertEqual(1, cfg.count("Port"))
        self.assertIn("Port {}".format(port), cfg)

    def test_sshd_port_not_claimed(self):
        svcs = open("/etc/services").read()
        port = self.defn["sshd.port"]
        self.assertNotIn(port, svcs)

    def test_keybased_authentication_is_enabled(self):
        cfg = open("/etc/ssh/sshd_config").read()
        self.assertEqual(1, cfg.count("\nRSAAuthentication"))
        self.assertEqual(1, cfg.count("\nPubkeyAuthentication"))
        self.assertIn("RSAAuthentication yes", cfg)
        self.assertIn("PubkeyAuthentication yes", cfg)

    def test_forwarding_is_disabled(self):
        cfg = open("/etc/ssh/sshd_config").read()
        self.assertEqual(1, cfg.count("AllowTcpForwarding"))
        self.assertEqual(1, cfg.count("X11Forwarding"))
        self.assertIn("AllowTcpForwarding no", cfg)
        self.assertIn("X11Forwarding no", cfg)

    def test_verbose_logging(self):
        cfg = open("/etc/ssh/sshd_config").read()
        self.assertEqual(1, cfg.count("LogLevel"))
        self.assertIn("LogLevel VERBOSE", cfg)

    def test_group_permission(self):
        cfg = open("/etc/ssh/sshd_config").read()
        self.assertEqual(1, cfg.count("AllowUsers"))
        self.assertIn("AllowUsers {}\n".format(self.defn["admin"]), cfg)

    def test_root_login(self):
        cfg = open("/etc/ssh/sshd_config").read()
        self.assertEqual(1, cfg.count("PermitRootLogin"))
        self.assertIn("PermitRootLogin no", cfg)

    def test_admin_user_has_public_key(self):
        auth_keys = os.path.join(
            os.path.expanduser("~{}".format(self.defn["admin"])),
            ".ssh", "authorized_keys")
        self.assertTrue(os.path.isfile(auth_keys))
        self.assertEqual(1, len(open(auth_keys).readlines()))

def imports():
    import os
    import inspect
    import platform
    import subprocess
    import sys
    import unittest

def operate(class_):
    try:
        channel.send("Executing from {}.".format(platform.node()))
        class_.ini = channel.receive()
        class_.args = channel.receive()
        class_.sudoPwd = channel.receive()
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

if __name__ == "__channelexec__":
    operate(OpenSSHChecks)


if __name__ == "__main__":
    from yardstick.cli import log_setup # Move
    from yardstick.cli import main
    from yardstick.cli import parser

    p = parser()
    args = p.parse_args()
    logName = log_setup(args, "check_access")
    if args.version:
        sys.stdout.write(__version__ + "\n")
        rv = 0
    else:
        ldr = unittest.defaultTestLoader
        testClasses = {
            type(meth) for mod in ldr.discover("yardstick.openrc")
            for suite in mod for meth in suite
        }

        for class_ in testClasses:
            importsLines, nr = inspect.getsourcelines(imports)
            operateLines, nr = inspect.getsourcelines(operate)
            operateLines[0] = 'if __name__ == "__channelexec__":\n'
            text = "\n".join((
                textwrap.dedent("".join(importsLines[1:])),
                inspect.getsource(class_),
                "".join(operateLines).replace("class_", class_.__name__)
            ))
            print(text)
            rv = main(text, args, logName)
            print("\n")
            print(
                *[i for a in ("skipped", "failures", "errors")
                    for i in rv[a]],
                sep="\n"
            )
            print("Total: {}".format(rv["total"]))

    sys.exit(1 if rv is None else 0)
