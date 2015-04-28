#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of yardstick.
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
# along with yardstick.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile
import textwrap
import unittest

from yardstick.ops.modder import config_parser
from yardstick.ops.modder import Text


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
        t = Text(
            sudoPass=None,
            path=None,
            seek=False,
            data=textwrap.dedent("""
                c.a = True
                c.b = False
            """).strip(),
            indent=4,
            newlines=1
        )
        op = t(TextTester.content, wd=None, sudo=False)
        msgd = list(op)
        self.assertEqual(expect, t._rv)

    def test_seek_true(self):
        change = textwrap.dedent("""
            c.a = True
            c.b = False
        """).strip()
        expect = "\n".join((
            TextTester.content,
            "\n".join(("    " + i for i in change.splitlines())),
            "", # newline = 1
        ))
        t = Text(
            sudoPass=None,
            path=None,
            seek=True,
            data=textwrap.dedent("""
                c.a = True
                c.b = False
            """).strip(),
            indent=4,
            newlines=1
        )
        op = t(TextTester.content, wd=None, sudo=False)
        mgs = list(op)
        self.assertEqual(expect, t._rv)

    def test_seek_re(self):
        expect = TextTester.content.replace(
            "# a.a = False", "a.a = True"
        )
        t = Text(
            sudoPass=None,
            path=None,
            seek="# a\\.a.+$",
            data="a.a = True",
            indent=4,
            newlines=1
        )
        op = t(TextTester.content, wd=None, sudo=False)
        mgs = list(op)
        self.assertEqual(expect, t._rv)

    def test_enter_checks_attributes(self):
        config = """
            [vimrc]
            sudo = False
            action = remote
            type = Text
            path = /root/.vimrc
            seek = .*
            data =
                set textwidth=79
                set shiftwidth=4
                set tabstop=4
                set expandtab
                set number
                set ruler
                set backspace=2

                syntax on
                set background=dark
                colorscheme desert
            indent = 0
            newlines = 0
        """
        ini = config_parser()
        ini.read_string(config)
        kwargs = Text.arguments(**ini["vimrc"])
        self.assertIsInstance(kwargs, dict)
        self.assertEqual(5, len(kwargs))
        self.assertNotIn("sudo", kwargs)
        self.assertNotIn("action", kwargs)
        self.assertNotIn("type", kwargs)


    def test_file_interaction(self):
        expect = TextTester.content.replace(
            "# a.a = False", "a.a = True"
        )
        fd, fP = tempfile.mkstemp(text=True)
        try:
            with open(fP, 'w') as target:
                target.write(TextTester.content)

            t = Text(
                sudoPass=None,
                path=fP,
                seek="# a\\.a.+$",
                data="a.a = True",
                indent=4,
                newlines=1
            )
            list(t(TextTester.content, wd=None, sudo=False))

            with open(fP, 'r') as target:
                rv = target.read()
                self.assertEqual(expect, rv)

        finally:
            os.close(fd)
            os.remove(fP)
