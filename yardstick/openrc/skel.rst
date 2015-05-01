
..  Titling
    ##++::==~~--''``

Skeleton files
==============

Before we manually edit any configuration, or create any new users, we need to
provide sensible `rc` files for a text editor (`vi` in this case).

Modifications
~~~~~~~~~~~~~

Root account
------------

On first boot, the `vi` editor available to us will be very basic. It reads the
`.exrc` file only.

`/root/.exrc`::

    set shiftwidth=4
    set tabstop=4
    set number

We'll also create a `/root/.vimrc` file for later when we have `vim`::

    set textwidth=79
    set shiftwidth=4
    set tabstop=4
    set expandtab
    set number
    set ruler
    set backspace=2

    syntax on
    set background=dark
    colorscheme desert

User accounts
-------------

We will modify `/etc/skel` so that new users get an account profile
suitable for a server environment.

Task definition
~~~~~~~~~~~~~~~

.. literalinclude:: skel.ini
   :language: ini
   :name: skel.ini
   :caption:

Tests
~~~~~

.. autoclass:: yardstick.openrc.test_skel.VimrcTests
.. autoclass:: yardstick.openrc.test_skel.SkelTests
