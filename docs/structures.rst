############
 Structures
############

Structures are ordered collections of fields, organizing data into a consistent format. They're
defined as Python classes, with fields as their attributes, in a pattern that's now fairly familiar
from other Python frameworks.

Discussing structures requirings including some fields, but for more information on how they work,
as well as specific field types, see :doc:`<fields>`.

**********************
 Structure Definition
**********************

A structure is defined by subclassing ``steel.Structure`` and declaring field attributes:

.. code:: python

   import steel

   class Header(steel.Structure):
      tag = steel.FixedBytes(b"DATA")
      major_version = steel.Integer(size=1)
      minor_version = steel.Integer(size=1)
      created_date = steel.Timestamp(tz="utc")
      title = steel.NullTerminatedString(encoding="ascii")

      @property
      def version(self) -> str:
          f"{obj.major_version}.{obj.minor_version}"

Each field in the structure corresponds to a piece of data that can be read or written in a
predictable format. The order of fields must match the order that the data appears in the original
format.

**********************************
 Working with Structure Instances
**********************************

Creating Instances
==================

You can create structure instances in several ways:

.. code:: python

   # Direct instantiation with keyword arguments
   packet = NetworkPacket(header=1234, message="Hello", checksum=0xABCD)

   # Empty instantiation and attribute assignment
   packet = NetworkPacket()
   packet.header = 1234
   packet.message = "Hello"
   packet.checksum = 0xABCD

Reading from Buffers
====================

Use the ``read()`` class method to parse binary data:

.. code:: python

   from io import BytesIO

   binary_data = b"\xd2\x04Hello\x00\xcd\xab\x00\x00"
   buffer = BytesIO(binary_data)
   packet = NetworkPacket.read(buffer)

   print(packet.header)    # 1234
   print(packet.message)   # "Hello"
   print(packet.checksum)  # 0xABCD

Writing to Buffers
==================

Use the ``write()`` method to serialize data back to binary format:

.. code:: python

   packet = NetworkPacket(header=1234, message="Hello", checksum=0xABCD)

   output = BytesIO()
   bytes_written = packet.write(output)

   binary_data = output.getvalue()
   print(f"Wrote {bytes_written} bytes")

************************
 Field Order and Layout
************************

Fields are processed in the order they're declared in the class definition. This determines both the
order of reading from buffers and writing to buffers:

.. code:: python

   class FileHeader(steel.Structure):
       magic = steel.FixedBytes(size=4)      # Read/written first
       version = steel.Integer(size=2)       # Read/written second
       flags = steel.Integer(size=2)         # Read/written third
       data_offset = steel.Integer(size=4)   # Read/written last

****************
 Error Handling
****************

If you try to access an attribute that wasn't set during instantiation, you'll get an
``AttributeError``:

.. code:: python

   packet = NetworkPacket(header=1234)  # Only header set
   print(packet.header)    # Works: 1234
   print(packet.message)   # Raises AttributeError

****************
 Advanced Usage
****************

Configuring all the fields in a structure
=========================================

Structures can be configured with global options that affect all fields on that structure.

.. code:: python

   class NetworkPacket(steel.Structure, endianness=">", encoding="ascii"):
       header = steel.Integer(size=2)  # Will encode big-endian values
       message = steel.TerminatedString()  # Will use ASCII encoding
       checksum = steel.Integer(size=4, endianness="<")  # Overrides to little-endian

.. note::

   Options specified on individual fields take priority over anything specified on the structure.

This is especially helpful for large structures that repeat a lot of the same kind of field, because
a format is typically consistent about how its data is represented. Configuring these options on the
structure itself can save a lot of duplication throughout the fields themselves.

.. warning::

   Not every field option can be specified on the structure. Consult the :doc:`fields` documentation
   for details about each field's behavior.

How missing values are handled
==============================

Because binary data doens't typically have headings for each value like JSON or YAML, there's often
no easy way to write the data out when values are missing. Therefore, the default behavior is to
raise an `AttributeError` when accessing any field that yet doesn't have a value, including when
writing to a data buffer.

Some fields can also have default values, which will allow you to write data even if you haven't
supplied a value for a given field. Check each field's documentation for details.

Configuration Access
====================

.. danger::

   While this may be useful for certain applications, `_config` is not yet a stable API. It's meant
   for internal use and shouldn't be necessary for the vast majority of Steel usage. It's included
   here for use cases that can't be handled any other way, for users who understand the risks and
   are willing to accept breakage in future releases.

Each structure class has a ``_config`` attribute that provides access to the field configuration,
which can be useful for introspection and dynamic field processing.

.. code:: python

   # Access all fields
   for name, field in Example._config.fields.items():
       print(f"Field {name}: {field.__class__.__name__}")

   # Access specific field
   integer_field = Example._config["integer"]
   print(f"Integer field size: {integer_field.size}")

This configuration option has the following attributes:

   -  ``fields`` is a dictionary of the fields that are specified on the structure. Because Python
      dictionaries are ordered by default, iterating over this dictionary -- or its keys or values
      individually -- will yield fields in the correct order.

   -  ``options`` is a dictionary of field options that were supplied at the structure level. This
      will contain everything that was supplied in the class definition, regardless of whether it
      actually overrode any pariticular field's configuration.
