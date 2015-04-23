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

from collections import OrderedDict
import difflib
import inspect
__doc__ = """
Checks the remote access configuration on a node.

::

    check_access.py < demo/manjaro_openrc_net-virtualbox.ini
"""

import os
import logging
import platform
import subprocess
import sys
import unittest as nodetest

try:
    from yardstick import __version__
except ImportError:
    # Remote host
    __version__ = None

        
class OpenSSHChecks(nodetest.TestCase):
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


if __name__ == "__channelexec__":
    try:
        channel.send("Executing from {}.".format(platform.node()))
        OpenSSHChecks.ini = channel.receive()
        OpenSSHChecks.args = channel.receive()
        OpenSSHChecks.sudoPwd = channel.receive()
        ldr = nodetest.defaultTestLoader
        suite = ldr.loadTestsFromTestCase(OpenSSHChecks)
        runner = nodetest.TextTestRunner(resultclass=nodetest.TestResult)
        rlt = runner.run(suite)
        rv = {a: [i[1] for i in getattr(rlt, a)]
                for a in ("errors", "failures", "skipped")}
        rv["total"] = rlt.testsRun
        channel.send(rv)
    except (EOFError, OSError) as e:
        channel.send(getattr(e, "args", e) or e)
    except (Error, Exception) as e:
        channel.send(getattr(e, "args", e) or e)
    finally:
        channel.send(None)


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
        rv = main(args, logName)

    #module = sys.modules[__name__]
    #for n, defn in enumerate(definitions(args.config)):
    #     with TestSession(module, defn, idn=n) as session:
    #         rv = session.operate()
    sys.exit(rv)
