Stand clear of the Pyon Cannon!
===============================

Contents:

.. toctree::
   :maxdepth: 2

* :ref:`genindex`
* :ref:`search`

Ops from fresh
==============

* .vimrc file for root
* modify /etc/skel
* check /etc/default/useradd
* /etc/hostname
* https://wiki.archlinux.org/index.php/General_recommendations

Passwords
=========

``apg -a 0 -m12``

Admin user
==========

::

    useradd --user-group --create-home devops
    useradd devops sudo