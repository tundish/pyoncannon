
..  Titling
    ##++::==~~--''``
    
The Pyon Cannon
:::::::::::::::

`Fire Python into the clouds!`

* A bundle of scripts to set up a Python node for web applications.
* Nothing to do with `Canon Pyon`_.

Yardstick
:::::::::

.. todo:: CLI

Simple check::

    yardstick check --ini manjaro_openrc_net-virtualbox.ini --paths yardstick/openrc/test_*.py

Simple check::

    yardstick check --ini manjaro_openrc_net-virtualbox.ini --modules yardstick.openrc.test_access

Discover available tags::

    yardstick units yardstick.common yardstick.openrc

Detect available test modules by tag::

    yardstick units --include=.. --exclude=.. yardstick.common yardstick.openrc

Make changes to remote host::

    yardstick auto --paths yardstick/openrc/stage01.py yardstick/openrc/stage02.py

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

.. _Canon Pyon: http://en.wikipedia.org/wiki/Canon_Pyon
.. _Execnet: https://pypi.python.org/pypi/execnet
.. _Git for Windows: http://git-scm.com/download/win
.. _GNU General Public License: http://www.gnu.org/licenses/gpl.html
