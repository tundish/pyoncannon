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

    data = textwrap.dedent("""
        set shiftwidth=4
        set tabstop=4
        set textwidth=79
        set expandtab
        set backspace=2
        set number
        set ruler
    """)

    ini = None
    settings = None
    args = None
    sudoPwd = None
    ts = None

    def test_root_exrc(self):
        self.assertTrue(os.path.isfile("/root/.exrc"))

    def test_root_vimrc(self):
        self.assertTrue(os.path.isfile("/root/.vimrc"))

    def tost_top_content(self):
        data = textwrap.dedent("""
            syntax enable   " enable syntax processing
        """)
        differ = difflib.SequenceMatcher(a=VimrcTests.data, b=data)
        self.assertAlmostEqual(differ.ratio(), 1.0, delta=0.09)
