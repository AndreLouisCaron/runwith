########################################
  runwith: poor man's shell operations
########################################

Description
===========

This Python library was created to use shell-like input/output direction in a
context where the execution environment doesn't support shell syntax.  It
provides a ``runwith`` executable that executes the command of your choice as a
sub-process in an execution environment prepared according to your desires.

The original use case is for use of Tox_ as a task runner.  Since Tox uses a
limited subset of shell capabilities and developers are not interested in
enhancing them (see `Capturing output from commands`_), I had to wrap some kind
of wrapper script.  I rapidly started reusing in other projects and making it
available on PyPI_ makes it easy to use like this:

.. source-code:: ini

   [testenv]
   deps =
     runwith
   commands =
     runwith -o foo.log -- foo

.. _Tox: https://tox.readthedocs.io/
.. _`Capturing output from commands`: http://comments.gmane.org/gmane.comp.python.testing.general/6709
.. _PyPI: https://pypi.python.org/pypi
