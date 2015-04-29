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
import unittest


class Text:

    @staticmethod
    def arguments(**kwargs):
        return {
            k: v for k, v in kwargs.items()
            if k in {
                "path", "seek", "data", "indent", "newlines"
            }
        }

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


class Command:

    @staticmethod
    def arguments(**kwargs):
        return kwargs.get("data", "")

    def __init__(
        self, name="yardstick.Command", **kwargs
    ):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.args = self.data.strip()

    def __call__(self, args, wd=None, sudo=False, sudoPwd=None):
        if sudo:
            p = subprocess.Popen(
                ["sudo", "-S"] + args,
                cwd=wd, shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL)
            self._out, self._err = p.communicate(
                "{}\n".format(self.sudoPwd).encode("utf-8"))
        else:
            p = subprocess.Popen(
                args,
                cwd=wd, shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL)
            self._out, self._err = p.communicate()

        for msg in (self._out, self.err):
            if msg.strip():
                yield log_message(logging.INFO, msg=msg, name=self.name)


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


def text2task(text, types):
    """
    Read a config section and return a Task.
    """
    which = {i.__name__: i for i in types}
    things = rson.loads(text)
    things = things if isinstance(things, list) else [things]
    return [which.get(i.pop("type", None), dict)(**i) for i in things]


def lockstep():
    """
    Executed on the target by the `auto` command.


    """
    logName="yardstick.lockstep"
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
            sec = ini.sections()[taskNr]
            msg = log_message(
                logging.INFO, msg="Task '{}'".format(sec),
                name=logName
            )
            channel.send(msg)
            #typ = __public__[data.pop("type", None)]
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


__public__ = {
    "file_write": None,
    None: None,
    }


__all__ = [
    "config_parser", "config_settings", "log_message",
] + list((i for i in __public__.keys() if i is not None)) 


if __name__ == "__channelexec__":
    lockstep()
