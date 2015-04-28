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

import logging
import os
import re
import tempfile
import textwrap
import unittest

from yardstick.ops.modder import log_message
from yardstick.ops.modder import config_parser

class Text:

    @staticmethod
    def arguments(**kwargs):
        return {k: v for k, v in kwargs.items()
                if k in {"path", "seek", "data", "indent", "newlines"}}

    def __init__(
        self, name="yardstick.Text", **kwargs
    ):
        self.name = name
        self._content = ""
        self._rv = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __call__(self, content, wd=None, sudo=False, sudoPwd=None):
        if self.path is not None:
            try:
                with open(self.path, 'r') as input_:
                    self._content = input_.read()
            except FileNotFoundError:
                pass

        if isinstance(self.seek, str):
            args = ([textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines)
            rObj = re.compile(self.seek, re.MULTILINE)
            match = rObj.search(content)
            if match:
                tgt = match.string[match.start():match.end()]
                msg = log_message(
                    logging.INFO,
                    msg="Pattern {} matched {}".format(
                        rObj.pattern, tgt),
                    name=self.name)
                self._rv = rObj.sub(self.data, content)
            else:
                msg = log_message(
                    logging.WARNING,
                    msg="Pattern {} unmatched.".format(
                        rObj.pattern),
                    name=self.name)
                self._rv = ""

            yield msg

        elif self.seek:
            args = ( 
                [content] +
                [textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines) 
            self._rv = "\n".join(args)
        else:
            args = ([textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines + [content])
            self._rv = "\n".join(args)

        if self._rv is not None and self.path is not None:
            with open(self.path, 'w') as output:
                output.write(self._rv)


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
        self.fail(Text.arguments(**ini["vimrc"]))


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
