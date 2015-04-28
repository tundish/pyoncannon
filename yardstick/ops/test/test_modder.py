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
import re
import textwrap
import unittest

from yardstick.ops.modder import log_message

class Text:

    def __init__(
        self, name="yardstick.Text", sudoPass=None, **kwargs
    ):
        self.name = name
        self.sudoPass = sudoPass
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __enter__(self):
        return self

    def __call__(self, content, wd=None, sudo=False):
        if isinstance(self.seek, str):
            rObj = re.compile(self.seek, re.MULTILINE)
            match = rObj.search(content)
            if match:
                tgt = match.string[match.start():match.end()]
                msg = log_message(
                    logging.INFO,
                    msg="Pattern {} matched {}".format(
                        rObj.pattern, tgt),
                    name=self.name)
            else:
                msg = log_message(
                    logging.WARNING,
                    msg="Pattern {} unmatched.".format(
                        rObj.pattern),
                    name=self.name)
            yield msg
            return "poo"
            return rObj.sub(self.data, content) + "\n"

        elif self.seek:
            args = ( 
                [content] +
                [textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines) 
            return "\n".join(args)
        else:
            args = ([textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines + [content])
            return "\n".join(args)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

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
            op = t(TextTester.content, wd=None, sudo=False)
            mgs = list(op)
            try:
                next(op)
            except StopIteration as e: 
                self.assertEqual(expect, e.value)

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
        with Text(
            sudoPass=None,
            path="/root/.vimrc",
            seek=True,
            data=textwrap.dedent("""
                c.a = True
                c.b = False
            """).strip(),
            indent=4,
            newlines=1
        ) as t:
            op = t(TextTester.content, wd=None, sudo=False)
            mgs = list(op)
            try:
                next(op)
            except StopIteration as e: 
                self.assertEqual(expect, e.value)
            rv = t(TextTester.content, wd=None, sudo=False)       

    def test_seek_re(self):
        expect = TextTester.content.replace(
            "# a.a = False", "a.a = True"
        )
        with Text(
            sudoPass=None,
            path="/root/.vimrc",
            seek="# a\\.a.+$",
            data="a.a = True",
            indent=4,
            newlines=1
        ) as t:
            op = t(TextTester.content, wd=None, sudo=False)
            mgs = list(op)
            try:
                next(op)
            except StopIteration as e: 
                self.assertEqual(expect, e.value)
            else:
                self.fail()

    def test_enter_checks_attributes(self):
        self.fail()
