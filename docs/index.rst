#######
 Steel
#######

Steel provides an elegant way to define binary data structures using Python, using classes and a
wide range of field definitions.

*************
 Quick Start
*************

.. code:: python

   import steel

   class Header(steel.Structure):
       title = steel.String(8)
       size = steel.Integer(2, endianness=">")

       def __init__(self, title: str, size: int):
           self.title = title
           self.size = size

   header = Header(title="Title", size=10)

************
 User Guide
************

.. toctree::
   :maxdepth: 2

   getting-started
   structures
   fields
