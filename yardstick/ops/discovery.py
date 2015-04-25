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
from collections.abc import MutableMapping
from collections.abc import MutableSequence

import pkg_resources

__doc__ = """
This module discovers

* file patterns in directories
  eg: yardstick/openrc/test_*.py
* entry points in installed packages
  eg: "opensshchecks = yardstick.openrc.test_openssl:OpenSSHChecks"

"""

def discover(id):
    for ep in pkg_resources.iter_entry_points(id):
        try:
            obj = ep.load(require=False)
        except Exception as e:
            continue
        else:
            yield (ep.name, obj)


testcases = OrderedDict(discover("yardstick.plugin.testcase"))
"""This is the collection of all installed test cases.
"""

operations = OrderedDict(discover("yardstick.plugin.operation"))
"""This is the collection of all installed test cases.
"""

if __name__ == "__main__":
    print(*["{:^10} {}".format(k, v) for k, v in globals().items()
          if isinstance(v, MutableMapping)
          or isinstance(v, MutableSequence)], sep="\n")
