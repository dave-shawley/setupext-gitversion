gitversion Setuptools Extension
===============================

|Version| |Downloads| |Status| |License|

Wait... Why? What??
-------------------
`PEP440`_ codifies a version scheme for Python packages.  This `setuptools`_
extension will generate `Developmental Release`_ and `Local Version Label`_
segments that identify the revision that is being built.  `PEP440`_ defines
the following format for Python package versions::

   version         = [epoch "!"] public-version ["+" local-version]
   epoch           = digit+
   public-version  = release-segment [pre-segment] [post-segment] [dev-segment]
   local-version   = (letter | digit)+ ["." (letter|digit)+]
   release-segment = digit+ ("." digit+)*
   pre-segment     = "a" digit+ | "b" digit+ | "rc" digit+
   post-segment    = ".post" digit+
   dev-segment     = ".dev" digit+

It also recommends that package indecies only accept *final releases* which
are defined as having a version that consists of only a release segment and
an optional epoch.  So why did I go through all of the trouble to create an
extension for managing versions that should not be submitted to a package
index?  If you develop Python packages that are used inside the walls of a
business, then you probably know exactly why -- using a local Python Package
Index that holds non-public packages is commonplace.  It is also common to
stage pre-release packages and builds from a CI server in an internal index.
This is where this extension comes into play.  It provides a consistent way
to manage package versions throughout all stages of development.

How?
----
The easiest way to use this extension is to install it into your build
environment and then use it from the command line when you generate and upload
your distribution.  It will generate the appropriate version segments and
update the package metadata appropriately.  That only solves half of the
problem -- the package name and embedded distribution metadata (as used by
the Python packaging tools) are re-written.  This means that:

1. *pip* will show the correct version
2. the package version retrieved from `pkg_resources`_ will be correct

What this extension does not do is magically provide a mechanism to update
a ``__version__`` attribute within your package or anything like that.  It
will write the generated version to a file that you can include in your
distribution though.  The recommended approach is to write your *setup.py*
to do this::

   import setuptools
   import mypackage

   try:
      with open('LOCAL-VERSION') as version_file:
         local_id = version_file.readline().strip()
   except IOError:
      local_id = ''

   setuptools.setup(
      name='mypackage',
      version=mypackage.__version__ + local_id,
      # all the other stuff
   )

You will also need to add ``include LOCAL-VERSION`` to your *MANIFEST.in* to
ensure that it is included in your distribution file.  If you need access to
the full version information, then you can embed the version file as package
data and look it up using ``pkgutil.get_data`` to build ``__version__``::

   # mypackage.__init__
   import pkgutil

   version_info = [1, 2, 3]
   __version__ = '.'.join(str(v) for v in version_info)
   try:
      with pkgutil.get_data(__name__, 'VERSION') as file_obj:
         suffix += file_obj.readline().strip()
      __version__ += suffix
      version_info.extend(suffix.replace('+', '.').split('.'))
   except IOError:
      pass

This approach will give you programmatic access to the full version information
from outside of your module.  If you do need such access, you are probably
much better off using the facilities provided by `pkg_resources`_::

   # mypackage.__init__
   version_info = (1, 2, 3)
   __version__ = '.'.join(str(v) for v in version_info)

   # package that needs version information
   try:
      import pkg_resources
      dist = pkg_resources.get_distribution('mypackage')
      version = dist.version
   except ImportError:
      import mypackage
      version = mypackage.__version__

There are many different ways to embed additional version information in
your package.  This extension will generate non-release version information
deterministically from git.  It is up to you to make use of it.

Ok... Where?
------------
+---------------+--------------------------------------------------------------+
| Source        | https://github.com/dave-shawley/setupext-gitversion          |
+---------------+--------------------------------------------------------------+
| Status        | https://drone.io/github.com/dave-shawley/setupext-gitversion |
+---------------+--------------------------------------------------------------+
| Download      | https://pypi.python.org/pypi/setupext-gitversion             |
+---------------+--------------------------------------------------------------+
| Documentation | http://setupext-gitversion.readthedocs.org/en/latest         |
+---------------+--------------------------------------------------------------+
| Issues        | https://github.com/dave-shawley/setupext-gitversion          |
+---------------+--------------------------------------------------------------+

.. _setuptools: https://pythonhosted.org/setuptools/
.. _PEP440: https://www.python.org/dev/peps/pep-0440
.. _Developmental Release: https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
.. _Local Version Label: https://www.python.org/dev/peps/pep-0440/#local-version-identifiers
.. _pkg_resources: https://pythonhosted.org/setuptools/pkg_resources.html#getting-or-creating-distributions

.. |Version| image:: https://badge.fury.io/py/setupext-gitversion.svg
   :target: https://badge.fury.io/
.. |Downloads| image:: https://pypip.in/d/setupext-gitversion/badge.svg?
   :target: https://pypi.python.org/pypi/setupext-gitversion
.. |Status| image:: https://drone.io/github.com/dave-shawley/setupext-gitversion/status.png
   :target: https://drone.io/github.com/dave-shawley/setupext-gitversion
.. |License| image:: https://pypip.in/license/dave-shawley/badge.svg?
   :target: https://setupext-dave-shawley.readthedocs.org/
