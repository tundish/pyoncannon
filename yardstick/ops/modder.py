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

import configparser
import logging
import platform
import re
import unittest

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
            channel.send(taskNr)
            taskNr = channel.receive()

    except (EOFError, OSError) as e:
        channel.send(str(getattr(e, "args", e) or e))
    except Exception as e:
        channel.send(str(getattr(e, "args", e) or e))
    finally:
        channel.send(None)


if __name__ == "__channelexec__":
    lockstep()
