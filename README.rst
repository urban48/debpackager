Overview
========

debpackager is a cli tool used for creating debain packages

Main Features:
 * project creation template (only python supported atm)
 * Provides easy control over project packaging process 
 * Version management in SemVer standard (http://semver.org/)  

Requirements
============

* Python 2.7
* Works on Linux

Dependencies
============
* dh-make

Install
=======

.. code-block:: shell

        sudo apt-get install dh-make

.. code-block:: shell

        pip install debpackager

Usage
=====

**start new project:** (only python supported right now)

.. code-block:: shell

    usage: debpackager --init [-h] [-p] project_name project_type

    positional arguments:
      project_name  supply project name
      project_type  supply project type

   optional arguments:
      -h, --help    show this help message and exit
      -p , --path   set path to the project, default: current location



**build**

.. code-block:: shell

    usage: debpackager build [-h] [--install-dependencies] [--no-clean] [-t] [-p] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      --install-dependencies
                            install deb dependencies before build (used for python virtualenv creation)
      --no-clean            leave behind everything used to create the debian package.
      -t , --type           set project type, default: auto detect
      -p , --path           set path to project, default: current location
      -v , --version        set version manually

Documentation
=============

see `wiki <https://github.com/urban48/debpackager/wiki>`_


Contributing
============

By participating in this project you agree to abide by its terms.