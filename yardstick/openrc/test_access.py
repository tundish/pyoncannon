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

"""

import os
import logging
import platform
import subprocess
import sys
import unittest

        
class OpenSSHChecks(unittest.TestCase):
    """
    https://help.ubuntu.com/community/SSH/OpenSSH/Configuring
    """
    #TODO: add sudoPass, etc

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
