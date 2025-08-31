#######
 Steel
#######

Steel provides an elegant way to define binary data structures using Python, using classes and a
wide range of field definitions.

**************
 Requirements
**************

-  Python 3.12+

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

***************
 Core Concepts
***************

Steel consists of two main features: structures and fields. Fields represent

Structures
==========

To be written

Fields
======

Fields are the building blocks of Steel structures. They define how data is encoded, decoded, and
validated.

All fields provide a set of :doc:`common functionality <fields/index>`, with a range of fields for
different data types:

.. toctree::
   :maxdepth: 2

   structures
   fields/index

More nuanced control over the data by accessing the data directly :doc:`as bytes <fields/bytes>`, or
you can create your own :doc:`custom fields <fields/custom-fields>` to support new or customized
data types.
