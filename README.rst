
..  Titling
    ##++::==~~--''``
    
About Yardstick
:::::::::::::::

Quick demo
==========

1. Start a fresh installation of `Manjaro OpenRC Net`_ inside `VirtualBox`_
   for Windows.

2. Install Execnet_::

    pyoncannon> pip install execnet

3. Run the checks against the VM::

    pyoncannon> python -m yardstick.ops.main @demo\check-manjaro_openrc_net-virtualbox.windows

4. Run the tasks against the VM::

    pyoncannon> python -m yardstick.ops.main @demo\auto-manjaro_openrc_net-virtualbox.windows

5. Run the checks again to show conformance::

    pyoncannon> python -m yardstick.ops.main @demo\check-manjaro_openrc_net-virtualbox.windows


Command line interface
======================

Run a check; modules identified by file path::

    yardstick check --ini manjaro_openrc_net-virtualbox.ini --paths yardstick/openrc/test_*.py

Run a check; name a package or module using dotted notation::

    yardstick check --ini manjaro_openrc_net-virtualbox.ini --modules yardstick.openrc.test_access

Make changes to remote host::

    yardstick auto --paths yardstick/openrc/stage01.py yardstick/openrc/stage02.py

Not yet implemented
~~~~~~~~~~~~~~~~~~~

Discover available tags::

    yardstick units yardstick.common yardstick.openrc

Detect available test modules by tag::

    yardstick units --include=.. --exclude=.. yardstick.common yardstick.openrc

Requirements
::::::::::::

* Python 3.4 or later.
* Execnet_.

Windows environment
===================

It is a project goal to support operation from MS Windows 8. For this OS, you
should install `Git for Windows`_ which bundles some GNU CLI tools and an
OpenSSH environment.

* During installation, allow Git to install the CLI tools into your ``PATH``.
* Set your ``HOME`` environment variable to ``%HOMEPATH%`` for SSH to work properly.

:Author: tundish
:Copyright: 2015 D Haynes
:Licence: `GNU General Public License`_

.. _Manjaro OpenRC Net: http://sourceforge.net/projects/manjaro-openrc/files/release/0.8.12/net/
.. _VirtualBox: https://www.virtualbox.org/
.. _Execnet: https://pypi.python.org/pypi/execnet
.. _Git for Windows: http://git-scm.com/download/win
.. _GNU General Public License: http://www.gnu.org/licenses/gpl.html
