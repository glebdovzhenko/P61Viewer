"""
ListWidgets
===========

Interface
---------

This sub-module interfaces two classes: :code:`EditableListWidget` and :code:`ActiveListWidget`.

- :code:`EditableListWidget` represents a list of datasets. Allows for group operations such as adding, deleting,
  changing active status.
- :code:`ActiveListWidget` represents a list of active datasets. Allows for having selected just one item at a time.

Implementation
--------------

.. automodule:: ListWidgets.ActiveListWidget
   :members:

.. automodule:: ListWidgets.EditableListWidget
   :members:
"""
from .ActiveListWidget import ActiveListWidget
from .EditableListWidget import EditableListWidget
