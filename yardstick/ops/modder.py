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

import configparser
import logging
import platform
import subprocess
import re
import textwrap
import time
import unittest


class Text:

    @staticmethod
    def arguments(**kwargs):
        rv = {
            "path": kwargs.get("path", ""),
            "seek": kwargs.get("seek", "False"),
            "data": kwargs.get("data", ""),
            "indent": int(kwargs.get("indent", "0")),
            "newlines": int(kwargs.get("newlines", "0")),
        }
        if rv["seek"] in ("True", "False"):
            rv["seek"] = bool(rv["seek"])
        return rv

    def __init__(
        self, name="yardstick.Text", **kwargs
    ):
        self._name = name
        self._content = ""
        self._rv = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __call__(self, content=None, wd=None, sudo=False, sudoPwd=None):
        if self.path is not None:
            try:
                with open(self.path, 'r') as input_:
                    self._content = input_.read()
            except FileNotFoundError:
                pass

        content = self._content if content is None else content
        if isinstance(self.seek, str):
            rObj = re.compile(self.seek, re.DOTALL | re.MULTILINE)
            match = rObj.search(content)
            if match:
                tgt = match.string[match.start():match.end()]
                msg = log_message(
                    logging.DEBUG,
                    msg="Pattern {} matched {}".format(
                        rObj.pattern, tgt),
                    name=self._name)
                self._rv = "\n".join(
                    [rObj.sub(textwrap.indent(self.data, ' ' * self.indent),
                     content, count=0)] +
                    [""] * self.newlines
                )
            else:
                msg = log_message(
                    logging.WARNING,
                    msg="Pattern {} unmatched.".format(
                        rObj.pattern),
                    name=self._name)
                self._rv = ""

            yield msg

        elif self.seek:
            args = (
                [content] +
                [textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines
            )
            self._rv = "\n".join(args)
        else:
            args = (
                [textwrap.indent(self.data, ' ' * self.indent)] +
                [""] * self.newlines + [content]
            )
            self._rv = "\n".join(args)

        # yield log_message(logging.DEBUG, msg=self._rv, name=self._name)

        if self._rv is not None and self.path is not None:
            with open(self.path, 'w') as output:
                output.write(self._rv)
                output.flush()


class Command:

    @staticmethod
    def arguments(**kwargs):
        return {"data": kwargs.get("data", "")}

    def __init__(
        self, name="yardstick.Command", **kwargs
    ):
        self._name = name
        for k, v in kwargs.items():
            setattr(self, k, v)
        self._args = self.data.strip().split()

    def __call__(self, args=None, wd=None, sudo=False, sudoPwd=None):
        args = self._args if args is None else args
        if sudo:
            p = subprocess.Popen(
                ["sudo", "-S"] + args,
                cwd=wd, shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL)
            yield log_message(logging.DEBUG, msg=str(p), name=self._name)
            self._out, self._err = p.communicate(
                "{}\n".format(sudoPwd).encode("utf-8"))
        else:
            p = subprocess.Popen(
                args,
                cwd=wd, shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL)
            self._out, self._err = p.communicate()

        for msg in (self._out, self._err):
            if msg is not None and msg.strip():
                yield log_message(
                    logging.INFO, msg=msg.decode("utf-8"), name=self._name
                )

class Wait(Command):

    @staticmethod
    def arguments(**kwargs):
        return {
            "interval": float(kwargs.get("interval", "2.0")),
            "limit": int(kwargs.get("limit", "60")),
            "data": kwargs.get("data", ""),
            "condition": kwargs.get("condition", None),
        }

    def __init__(
        self, name="yardstick.Wait", **kwargs
    ):
        super().__init__(name, **kwargs)

    def __call__(self, args=None, wd=None, sudo=False, sudoPwd=None):
        if not self.data or self.condition is None:
            time.sleep(self.interval)
            return

        n = 0
        match = None
        rObj = re.compile(self.condition, re.MULTILINE)
        while match is None and n < self.limit:
            time.sleep(self.interval)
            for result in super().__call__(args, wd, sudo, sudoPwd):
                yield result
                match = rObj.search(result["msg"])
            n += 1

def config_parser():
    rv = configparser.ConfigParser(
        strict=True,
        empty_lines_in_values=True,
        allow_no_value=True,
        interpolation=configparser.ExtendedInterpolation()
    )
    rv.SECTCRE = re.compile(r"\[ *(?P<header>[^]]+?) *\]")
    return rv


def config_settings(ini):
    # TODO: check defaults section
    return ini.defaults()


def log_message(lvl, msg, *args, **kwargs):
    msg = logging.LogRecord(
        name=kwargs.get("name", "unknown"),
        level=lvl,
        pathname="",
        lineno="",
        msg=msg,
        args=args,
        exc_info=None,
    )
    return vars(msg)


def lockstep():
    """
    Executed on the target by the `auto` command.


    """
    logName = "yardstick.lockstep"
    try:
        msg = log_message(
            logging.INFO,
            msg="Executing from {}.".format(platform.node()),
            name=logName)
        channel.send(msg)

        config = channel.receive()
        try:
            ini = config_parser()
            ini.read_string(config)
            settings = config_settings(ini)
        except Exception as e:
            ini = None
            settings = {}
            channel.send(config)
            channel.send(str(getattr(e, "args", e) or e))

        args = channel.receive()
        sudoPwd = channel.receive()
        ts = channel.receive()

        taskNr = channel.receive()
        while taskNr is not None:
            secName = ini.sections()[taskNr]
            msg = log_message(
                logging.INFO, msg="Task '{}'".format(secName),
                name=logName
            )
            channel.send(msg)

            section = ini[secName]
            sudo = section.getboolean("sudo", fallback=False)
            typ = section.get("type", fallback=None)
            Op = {i.__name__: i for i in (Command, Text, Wait)}.get(typ, None)
            if any(i is None for i in (sudo, typ, Op)):
                msg = log_message(
                    logging.ERROR, msg="Bad parameters.",
                    name=logName
                )
                channel.send(msg)
            else:
                op = Op(**Op.arguments(**section))
                for msg in op(sudo=sudo, sudoPwd=sudoPwd):
                    channel.send(msg)

            channel.send(taskNr)
            taskNr = channel.receive()

    except (EOFError, OSError) as e:
        channel.send(
            log_message(
                logging.ERROR,
                msg=str(getattr(e, "args", e) or e),
                name=logName)
        )
    except Exception as e:
        channel.send(
            log_message(
                logging.ERROR,
                msg=str(getattr(e, "args", e) or e),
                name=logName)
        )
    finally:
        channel.send(None)


if __name__ == "__channelexec__":
    lockstep()
