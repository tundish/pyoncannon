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

import difflib
import os
import textwrap
import unittest


class VimrcTests(unittest.TestCase):
    """
    Checks for .exrc and .vimrc files in:

    * `/root`
    * `/etc/skel`

    """

    exrc = textwrap.dedent("""
        set shiftwidth=4
        set tabstop=4
        set number
    """).strip()

    ini = None
    settings = None
    args = None
    sudoPwd = None
    ts = None

    def test_root_exrc(self):
        self.assertTrue(os.path.isfile("/root/.exrc"))
        with open("/root/.exrc", 'r') as rc:
            content = rc.read().splitlines()

        for line in (i.strip() for i in VimrcTests.exrc.splitlines()):
            with self.subTest(line=line):
                self.assertIn(line, content)

    def test_root_vimrc(self):
        self.assertTrue(os.path.isfile("/root/.vimrc"))
