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

import argparse
import inspect
import ipaddress
import logging
import logging.handlers
import os
import os.path
import subprocess
import sys
import time
import unittest

import execnet

import yardstick.ops.checker
import yardstick.ops.modder

__doc__ = """

The yardstick program supports system administration of remote nodes.

It lets you select and launch:

* tests written in Python
* modification tasks controlled by a `.ini` file

"""

DFLT_IDENTITY = os.path.expanduser(os.path.join("~", ".ssh", "id_rsa"))
DFLT_PORT = 22
DFLT_USER = "root"
KNOWN_HOSTS = os.path.expanduser(os.path.join("~", ".ssh", "known_hosts"))


def forget_host(host):
    subprocess.check_call(["ssh-keygen", "-f", KNOWN_HOSTS, "-R", host])


def execnet_string(ini, args):
    settings = yardstick.ops.modder.config_settings(ini)
    port = args.port or settings["admin.port"] or DFLT_PORT
    user = args.user or settings["admin.user"] or DFLT_USER
    host = args.host or ipaddress.ip_interface(settings["admin.net"]).ip
    python = args.python or settings["admin.python"] or sys.executable

    if host in (None, "0.0.0.0", "127.0.0.1", "localhost"):
        rv = "popen//dont_write_bytecode"
    else:
        rv = ("ssh=-i {identity} -p {port} {user}@{host}"
         "//python={python}").format(
            identity=os.path.expanduser(args.identity),
            host=host, port=port, user=user, python=python
        )
    return rv

def log_setup(args, name="yardstick"):
    log = logging.getLogger(name)

    log.setLevel(args.log_level)

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-7s %(name)s|%(message)s")
    ch = logging.StreamHandler()

    if args.log_path is None:
        ch.setLevel(args.log_level)
    else:
        fh = logging.handlers.WatchedFileHandler(args.log_path)
        fh.setLevel(args.log_level)
        fh.setFormatter(formatter)
        log.addHandler(fh)
        ch.setLevel(logging.WARNING)

    ch.setFormatter(formatter)
    log.addHandler(ch)
    return name


def gen_auto_tasks(args):
    for spec in args.modules:
        mod = None # FIXME:
        yield mod
    yield yardstick.ops.modder

 
def gen_check_tasks(args):
    ldr = unittest.defaultTestLoader
    testClasses = {
        type(meth)
        for i in args.modules + args.paths
        for mod in ldr.discover(i)
        for suite in mod for meth in suite
    }

    for class_ in testClasses:
        checkLines, nr = inspect.getsourcelines(
            yardstick.ops.checker.check
        )
        checkLines[0] = 'if __name__ == "__channelexec__":\n'
        text = "\n".join((
            yardstick.ops.checker.shebang,
            "\n".join("import {}".format(i)
                      for i in yardstick.ops.checker.imports),
            "",
            inspect.getsource(class_),
            inspect.getsource(yardstick.ops.modder.config_parser),
            inspect.getsource(yardstick.ops.modder.config_settings),
            inspect.getsource(yardstick.ops.modder.log_message),
            "".join(checkLines).replace("class_", class_.__name__)
        ))
        yield text


def loop_over_lockstep(channel, name, ini):
    log = logging.getLogger(name)

    for n, s in enumerate(ini.sections()):
        log.debug(s)
        if ini.get(s, "action", fallback="remote") == "local":
            log.debug("Section {} needs local action.".format(n))
        else:
            channel.send(n)
            loop_over_logrecords(channel, name, n)

    channel.send(None)
    return len(ini.sections())


def loop_over_logrecords(channel, name, sentinel=None):
    log = logging.getLogger(name)

    prev = msg = channel.receive()
    while not msg == sentinel:
        try:
            record = logging.makeLogRecord(msg)
            log.handle(record)
        except:
            log.debug(msg)
        finally:
            prev, msg = msg, channel.receive()

    return prev


def operate(code, config, args, sudoPwd, name="yardstick"):
    log = logging.getLogger(name)

    ini = yardstick.ops.modder.config_parser()
    ini.read_string(config)
    settings = yardstick.ops.modder.config_settings(ini)

    if args.forget:
        host = ipaddress.ip_interface(settings["admin.net"])
        forget_host(host.ip.compressed)
        forget_host(host.ip.exploded)

    rv = None
    s = execnet_string(ini, args)
    log.debug(s)
    if s.startswith("popen"):
        log.warning("Local invocation.")

    if args.debug:
        os.environ["EXECNET_DEBUG"] = "2"

    try:
        gw = execnet.makegateway(s)
    except BrokenPipeError:
        log.error(
            "Unable to connect to host: "
            "Check your hypervisor and/or networking."
        )
        return rv

    try:
        ch = gw.remote_exec(code)
        ch.send(config)
        ch.send({k: v for k, v in vars(args).items() if not isinstance(v, list)})
        ch.send(sudoPwd)
        ch.send(time.time())

        if code is yardstick.ops.modder:
            rv = loop_over_lockstep(ch, name, ini)
        else:
            rv = loop_over_logrecords(ch, name)

    except (EOFError, OSError) as e:
        log.error(s)
    except Exception as e:
        log.error(getattr(e, "args", e) or e)
    finally:
        gw.exit()

    return rv
