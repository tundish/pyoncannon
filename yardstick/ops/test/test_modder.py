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

import re
import textwrap
import unittest

#from yardstick.ops.modder import Text

class Text:

    def __init__(self, sudoPass=None, **kwargs):
        self.sudoPass = sudoPass
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __enter__(self):
        return self

    def __call__(self, content, wd=None, sudo=False):
        if isinstance(self.seek, str):
            return None
        elif self.seek:
            return None
        else:
            args = ([textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines + [content])
            return "\n".join(args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def success(self, rv):
        return bool(rv)


class TextTester(unittest.TestCase):

    content = textwrap.dedent("""
        # a.a = False
        b.a = True
        b.b = "default"
    """).lstrip()

    def test_seek_false(self):
        change = textwrap.dedent("""
            c.a = True
            c.b = False
        """).strip()
        expect = "\n".join((
            "\n".join(("    " + i for i in change.splitlines())),
            "", # newline = 1
            TextTester.content
        ))
        with Text(
            sudoPass=None,
            path="/root/.vimrc",
            seek=False,
            data=textwrap.dedent("""
                c.a = True
                c.b = False
            """).strip(),
            indent=4,
            newlines=1
        ) as t:
            rv = t(TextTester.content, wd=None, sudo=False)       
        self.assertEqual(expect, rv)

    def test_seek_true(self):
        expect = TextTester.content + """
        c = True

        """
        self.fail(None)

    def test_seek_re(self):
        expect = TextTester.content.replace(
            "# a.a = False", "a.a = True"
        )
        self.fail(expect)

    def test_enter_checks_attributes(self):
        self.fail()
