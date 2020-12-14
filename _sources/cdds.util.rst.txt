cdds.util
=========

The util module contains some utility functions that have no good place elsewhere but are not for internal use only (otherwise they would live in cdds.internal). 
It is preferred you import the functions from the submodules directly.

.. code-block:: python

   from cdds.util.time import duration
   from cdds.util.entity import isgoodentity


.. autofunction:: cdds.util.entity.isgoodentity

.. autofunction:: cdds.util.time.duration