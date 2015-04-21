Stand clear of the Pyon Cannon!
===============================

Contents:

.. toctree::
   :maxdepth: 2

* :ref:`genindex`
* :ref:`search`

SSH Access
==========

Set up a `host-only network`_ for the VM.

Log in to the VM as root, and check what services are running::

    # rc-status -s
    
If necessary, start sshd::

    # service sshd start
    
Set `sshd` to start on boot::

    # rc-update add sshd default

Find the IP address of the running VM::

    # ifconfig eth1

Use the host-accessible IP (192.168.56.101 in this case) to copy your SSH public key into the root account
of the new VM::

    > cd %HOME%
    > ssh root@192.168.56.101 "umask 077; test -d .ssh || mkdir .ssh ; cat >> .ssh/authorized_keys || exit 1" < .ssh\id_rsa.pub
    root@192.168.56.101's password:
    Authenticated to 192.168.56.101 ([192.168.56.101]:22).

Test SSH access from the host::

    >ssh root@192.168.56.101
    Enter passphrase for key '.ssh/id_rsa':
    [root@manjaro ~]#


Static IP Address
=================

Ops from fresh
==============

* .vimrc file for root
* .bashrc ``export EDITOR=vi``
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
    
.. _host-only network: https://www.virtualbox.org/manual/ch06.html#network_hostonly
.. _openrc tutorial: http://big-elephants.com/2013-01/writing-your-own-init-scripts/