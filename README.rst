Overview
========

debpackager is a cli tool used for creating debain packages
inspired by `fpm <https://github.com/jordansissel/fpm>`_ and `maven <https://maven.apache.org/i>`_

Main Features:

 * Provides easy control over project packaging process using configuration     
   file called project.json (like pom.xml in maven)
 * Easy addition of new packing policies for different project types and languages
 * Solves the problem of python projects need debian dependencies to run.  
 * Making your code a Linux compatible daemon with just few simple steps
 * Greatly simplifies the packaging and deployment process. 
 * Package version management in SemVer standard (http://semver.org/) 

What does it do
===============
Creates only debian binary packages right now.
Do not really follow Debian packaging policy or all the packaging guidelines.
Provides an easy way to configure, manage and create a deb package that can be deployed
on Linux.


Requirements
============
* Python >=2.7
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

Must have `project.json <https://github.com/urban48/debpackager/wiki/conventions-and-usage#projectjson>`_ at your project root directory

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

See `wiki <https://github.com/urban48/debpackager/wiki>`_


Contributing
============

By participating in this project you agree to abide by its terms.
