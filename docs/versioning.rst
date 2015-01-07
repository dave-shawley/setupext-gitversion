Version Calculation
===================
:pep:`440` defines a Python Package's version using the following grammar.

.. productionlist::
   version: [`epoch` "!"] `public` ["+" `local`]
   epoch: `digit`+
   public: `release` [`pre`][`post`][`dev`]
   release: `digit`+ ("." `release`)*
   pre: "pre" `digit`+
   post: "post" `digit`+
   dev: "dev" `digit`+
   local: (`letter` | `digit`)+ ("." `local`)*

Public Version
--------------
The public portion of the version identifier is managed by your package.  The
best practice for managing the public version is to simply embed it within your
package as a top-level attribute named ``__version__`` or ``version``.  You
should use the version attribute to calculate the value passed to as the
``version`` keyword to :func:`setuptools.setup`.

.. code-block:: python

   # setup.py
   import setuptools
   import mypackage

   setup(
      name='mypackage',
      version=mypackage.__version__,
      # ...
   )

This extension searches for a git tag matching the public portion of the
``version`` keyword and uses it as the basis for constructing the post and
development release segements.

Pre Release Segment
-------------------
This extension does not define a value for the pre-release segment.

Post Release Segment
--------------------
This extension defines the post-release segment as the number of merges
since the tag associated with your package's version.

Development Release Segment
---------------------------
This extension defines the development release segment as the number of
commits since the last merge.

Local Segment
-------------
This extension defines the local identifier as the first seven characters
of the most recent commit.  The local identifier is only included if the
``--committish`` flag is included and either the post or development 
segment is defined.
