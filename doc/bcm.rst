.. _bcm:

Broadcast Manager
=================

.. module:: can.broadcastmanager

The broadcast manager allows the user to setup periodic message jobs.
For example sending a particular message at a given period. The broadcast
manager supported natively by several interfaces and a software thread
based scheduler is used as a fallback.

This example shows the socketcan backend using the broadcast manager:

.. literalinclude:: ../examples/cyclic.py
    :language: python
    :linenos:


Message Sending Tasks
~~~~~~~~~~~~~~~~~~~~~

The class based api for the broadcast manager uses a series of
`mixin classes <https://www.ianlewis.org/en/mixins-and-python>`_.
All mixins inherit from :class:`~can.CyclicSendTaskABC`
which inherits from :class:`~can.CyclicTask`.

.. autoclass:: can.CyclicTask
    :members:

.. autoclass:: can.CyclicSendTaskABC
    :members:

.. autoclass:: can.LimitedDurationCyclicSendTaskABC
    :members:

.. autoclass:: can.MultiRateCyclicSendTaskABC
    :members:

.. autoclass:: can.ModifiableCyclicTaskABC
    :members:

.. autoclass:: can.RestartableCyclicTaskABC
    :members:


Functional API
--------------

.. warning::
    The functional API in :func:`can.send_periodic` is now deprecated
    and will be removed in version 4.0.
    Use the object oriented API via :meth:`can.BusABC.send_periodic` instead.

.. autofunction:: can.send_periodic
