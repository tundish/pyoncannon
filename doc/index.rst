
..  Titling
    ##++::==~~--''``
    
Stand clear of the Pyon Cannon!
===============================

Contents:

.. toctree::
   :maxdepth: 2

* :ref:`genindex`
* :ref:`search`

Initialisation file
===================

Make a `.ini format`_ file like this::

    [DEFAULT]
    hash = #
    admin.net = 192.168.56.10/24
    admin.gw = 192.168.56.101
    admin.if = eth1

SSH Access
==========

Set up a `host-only network`_ for the VM.

Log in to the VM as root, and check what services are running::

    # rc-status -s
    
If necessary, start sshd::

    # rc-service sshd start
    
Set `sshd` to start on boot::

    # rc-update add sshd default

Find the IP address of the running VM::

    # ip addr show eth1

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

Obtain the IP address of the host-only network adapter (eg: 192.168.56.1).

Pick a permanent address for the VM which is on the same subnet but outside the VirtualBox DHCP
address pool, (eg: 192.168.56.10 netmask 255.255.255.0).

* `Network sequencing`_
* netifrc_

Change on the fly
~~~~~~~~~~~~~~~~~

Take down the existing link, then apply the new address and bring the interface
up again::

    # ip link set eth1 down
    # ip addr add 192.168.56.10/24 dev eth1
    # ip link set eth1 up

Edit /etc/conf.d/net
~~~~~~~~~~~~~~~~~~~~

**This doesn't yet work**::

    # vi /etc/conf.d/net

Add the lines::

    config_eth0="dhcp"
    config_eth1="192.168.56.10/24"
    routes_eth1="default via 192.168.56.101"

Add interfaces
~~~~~~~~~~~~~~

Add interfaces::

    # cd /etc/init.d
    # ln -s net.lo net.eth0
    # ln -s net.lo net.eth1

Then::

    # rc-update del NetworkManager

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

Devops user
===========

::

    useradd --user-group --create-home devops
    useradd devops sudo

.. _.ini format: https://docs.python.org/3/library/configparser.html#supported-ini-file-structure    
.. _host-only network: https://www.virtualbox.org/manual/ch06.html#network_hostonly
.. _openrc tutorial: http://big-elephants.com/2013-01/writing-your-own-init-scripts/
.. _network sequencing: https://blog.flameeyes.eu/2012/10/may-i-have-a-network-connection-please#gsc.tab=0
.. _netifrc: https://forum.manjaro.org/index.php?topic=22241.0
