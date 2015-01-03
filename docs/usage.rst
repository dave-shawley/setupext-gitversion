Usage
=====

Command Line Synopsis
---------------------
.. program:: setup.py git_version

**Usage:** :program:`setup.py git_version` *[options]* *packaging-command*

The :program:`git_version` setuptools command updates the package's version
metadata based on repository information.  Since the update is only done on
the metadata in-memory, this is only really useful in the same *setup.py*
execution as a packaging command such as ``sdist`` or one of the ``bdist``
variants.

.. option:: -V FILE, --version-file FILE

   Writes the local segment of the version to *FILE* in addition to
   setting the in-memory version.

setup.cfg Example
-----------------
.. code-block:: guess
   
   [git_version]
   version-file = LOCAL-VERSION
