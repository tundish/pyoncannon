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
from io import StringIO
import sys
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

    def test_top_content(self):
        data = textwrap.dedent("""
            syntax enable   " enable syntax processing
        """)
        differ = difflib.SequenceMatcher(a=VimrcTests.data, b=data)
        print(differ.get_opcodes())
        self.assertAlmostEqual(differ.ratio(), 1.0, delta=0.09)

    def test_module_concatenation(self):
        print(inspect.getsource(VimrcTests))
        module = sys.modules[__name__]
        print(inspect.getsource(module))
        #print([i for i in sys.modules if i not in sys.builtin_module_names])
        print([i for i in sys.modules if i not in __builtins__])
