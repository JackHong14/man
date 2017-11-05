|Build Status|

man
===

``man`` is a software distribution tool that works over setuptools and
help integerate PyPi, Travis, Github and You together. This lets you
create a python library and have it deployed in less than ten minutes.

Getting started
---------------

Creation
~~~~~~~~

Say that you have an idea of a new library that you would like to share
with other on PyPi. You know python, you use github and you don't want
to spend hours struggling in the mess of package distribution.

Thus, just install ``man``:

::

    pip install man 

NOTE: If you are on windows, you will need to install ``pyreadline``
with ``pip install pyreadline``.

And create a new library:

::

    man new-lib

Then answer the short questions about your library:

::

    Name of your library:
    Short description:
    Keywords (space separated): 
    Full name:
    E-Mail:
    Github username:
    PyPi username:

If you don't already have a PyPi account, you need to `create
one <https://pypi.python.org/pypi?%3Aaction=register_form>`__.

Then you will be prompted for your github password to create a new
repository with the name of your lib.

Then you just need to: - Setup Travis: - `create an
account <https://travis-ci.org/>`__ - Find your repo at
https://travis-ci.org/profile/YOURNAME and turn the switch on. - Add
your travis password to the .travis.yml: - Open ``bash`` - And just run
``travis encrypt --add deploy.password`` - And type your travis password
- Add classifiers (or tags) for your library so people can find it more
easily, run ``man add tag`` - Write your code, do commits, tests and
whatever you want. - Complete the readme.md (not the readme.rst, because
it is always converted from the readme.md.)

First release
~~~~~~~~~~~~~

Now the version of your code is ``0.0.0``. I choose to use the simple
``MAJOR.MINOR.PATCH`` system as it's easy to use, understand and work
with.

When you are ready for your first release, type

::

    man release major

Enter a description of your first release (it can be more than one line)
and confirm that you want to create a new release. Your code is then
taged with ``v1.0.0``, and that will trigger a Travis build and
deployment on PyPi. You can go on
`travis-ci.org <https://travis-ci.org/>`__\ and when everything is
finished, type:

::

    pip install my-new-lib

And that's it!

And after
~~~~~~~~~

Then, everytime you add functionalities or correct bugs and you want to
share them just type one of the following:

::

    man release patch  # When you just fix broken things
    man release minor  # when you add functionnality
    man release major  # when you do big changes (maybe not backward compatible)

All commands are well described, so try to run them with the ``--help``
flag to see what ``man`` can do.

List of commands:
-----------------

Id there is a tilde (``~``) after a command, there is an interactive
prompt disponible, with autocompletion.

``man`` - ``add`` - ``keywords [KW1] [KW2] ...`` -
``package [PATH_TO_PKG]`` - ``dependancy [LIBRARY] [VERSION]`` ~ -
``script`` ~ - ``tag`` ~ - ``remove`` - ``keywords`` ~ -
``package [PKG_NAME]`` ~ - ``dependancy [LIBRARY]`` ~ -
``script [NAME]`` ~ - ``tag`` ~ - ``release [major|minor|patch]`` -
``--test`` - ``--again`` - ``new [DESTINATION_DIR]`` ~ - ``changelog`` -
``-v`` / ``--verbose`` - ``config`` ~ - See the ``pyconfiglib``
`reference <https://github.com/ddorn/pyconfiglib>`__. - ``gen`` -
``readme.rst`` - ``setup.py`` - ``MANIFEST.in``

--------------

By Diego Dorn

.. |Build Status| image:: https://travis-ci.org/ddorn/man.svg?branch=v1.5.1
   :target: https://travis-ci.org/ddorn/man
