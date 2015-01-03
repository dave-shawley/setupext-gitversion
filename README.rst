gitversion Setuptools Extension
===============================

|Version| |Downloads| |Status| |License| |Docs|

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

Let's look at the state of this project as I am writing this document.  The
git history looks like the following::

   * 3fdc192 - (HEAD, origin/initial-implementation, initial-implementation)
   ###### 9 more commits here
   * 7ca1fd2 - (origin/master, master)
   *   87d944e - Merge pull request #1 from dave-shawley/reorg (6 days ago)
   |\
   | * 04d0cca - (origin/reorg, reorg)
   | ###### 9 more commits here
   |/
   * bd7ad3c - (tag: 0.0.0) SYN (4 months ago)

When I run **setup.py git_version** it sets the version to ``0.0.0.post1.dev11``.
The ``0.0.0`` portion is the release segment that is passed to the ``setup``
function in *setup.py*.   The extension finds that tag in the history and
counts the number of merges that have occurred since that tag -- this value
becomes the *post* version segment.  In this case there has only been a single
merge.  Then it counts the number of commits since the last merge occurred --
this value becomes the *development* version segment.

How?
----
The easiest way to use this extension is to install it into your build
environment and then use it from the command line when you generate and upload
your distribution.

1. ``pip install setupext-gitversion`` into your build environment
2. Add the following lines to your *setup.cfg*::

     [git_version]
     version-file = LOCAL-VERSION

3. Add the following line to your *MANIFEST.in*::

      include LOCAL-VERSION

4. Modify your *setup.py* to append the contents of *LOCAL-VERSION*
   to your ``version`` keyword::

      version_suffix = ''
      try:
         with open('LOCAL-VERSION') as f:
            version_suffix = f.readline().strip()
      except IOError:
         pass

      setup(
         # normal keywords
         version='1.2.3' + version_suffix,
      )

   Where ``1.2.3`` is the tag of the last release package.

5. Add ``git_version`` to your *upload* or distribution generation
   command.  You want to use something like the following::

      setup.py git_version sdist upload
      setup.py git_version bdist_egg upload

And that's it.  That will embed SCM information into your package when
your build a distribution.  It is also smart enough to generate an empty
suffix for a build from a tagged commit.

Ok... Where?
------------
+---------------+--------------------------------------------------------------+
| Source        | https://github.com/dave-shawley/setupext-gitversion          |
+---------------+--------------------------------------------------------------+
| Status        | https://travis-ci.org/dave-shawley/setupext-gitversion       |
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

.. |Version| image:: https://pypip.in/version/setupext-gitversion/badge.svg
   :target: https://pypi.python.org/pypi/setupext-gitversion
.. |Downloads| image:: https://pypip.in/download/setupext-gitversion/badge.svg
   :target: https://pypi.python.org/pypi/setupext-gitversion
.. |Status| image:: https://travis-ci.org/dave-shawley/setupext-gitversion.svg
   :target: https://travis-ci.org/dave-shawley/setupext-gitversion
.. |License| image:: https://pypip.in/license/setupext-gitversion/badge.svg
   :target: http://opensource.org/licenses/BSD-3-Clause
.. |Docs| image:: https://readthedocs.org/projects/setupext-gitversion/badge/?version=latest
   :target: https://setupext-gitversion.readthedocs.org/
