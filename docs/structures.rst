############
 Structures
############

Structures are ordered collections of fields, organizing data into a consistent format. They're
defined as Python classes, with fields as their attributes, in a pattern that's now fairly familiar
from other Python frameworks.

Discussing structures requirings including some fields, but for more information on how they work,
as well as specific field types, see :doc:`fields`.

**********************
 Structure Definition
**********************

A structure is defined by subclassing ``steel.Structure`` and declaring field attributes:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

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

   import steel
   from io import BytesIO

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   binary_data = b"\xd2\x04Hello\x00\xcd\xab"
   buffer = BytesIO(binary_data)
   packet = NetworkPacket.read(buffer)

   print(packet.header)    # 1234
   print(packet.message)   # "Hello"
   print(packet.checksum)  # 0xABCD

Writing to Buffers
==================

Use the ``write()`` method to serialize data back to binary format:

.. code:: python

   import steel
   from io import BytesIO

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

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

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)        # Read/written first
       message = steel.NullTerminatedString(encoding="ascii")  # Read/written second
       checksum = steel.Integer(size=2)      # Read/written third

****************
 Error Handling
****************

If you try to access an attribute that wasn't set during instantiation, you'll get an
``AttributeError``:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   packet = NetworkPacket(header=1234)  # Only header set
   print(packet.header)    # Works: 1234
   print(packet.message)   # Raises AttributeError

************
 Validation
************

Structures support basic validation to ensure all field values conform to their expected formats and
constraints. This helps catch data integrity issues before writing to buffers or after reading from
potentially corrupted data.

Basic Validation
================

Use the ``validate()`` method to check that all fields in a structure contain valid values:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   packet = NetworkPacket(header=1234, message="Hello", checksum=0xABCD)
   packet.validate()  # Raises ValidationError if any field is invalid

The validation process checks each field according to its specific constraints:

-  **Integer fields** validate that values fit within their size and sign constraints
-  **String fields** validate encoding compatibility and length requirements
-  **Byte fields** validate exact size matches and content constraints
-  **Enum fields** validate that values belong to the specified enum class

Handling Validation Errors
==========================

When validation fails, a ``ValidationError`` is raised with details about the problem:

.. code:: python

   import steel
   from steel.fields.base import ValidationError

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   packet = NetworkPacket(header=70000, message="Hello", checksum=0xABCD)  # Header too big

   try:
       packet.validate()
   except ValidationError as e:
       print(f"Validation failed: {e}")

Common validation scenarios that raise errors:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   # Integer too large for field size
   packet = NetworkPacket(header=70000, message="Hello", checksum=0xABCD)  # header is 2-byte field
   packet.validate()  # ValidationError: value exceeds maximum

   # String encoding issues
   packet = NetworkPacket(header=1234, message="héllo", checksum=0xABCD)  # non-ASCII in ASCII field
   packet.validate()  # ValidationError: invalid encoding

Validation with Missing Fields
==============================

If a field hasn't been assigned a value, validation will also raise a ``ValidationError``:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   packet = NetworkPacket(header=1234)  # Missing message and checksum
   packet.validate()  # ValidationError

This ensures that all required fields are present before attempting to write the structure to a
buffer.

Validating After Reading
========================

Validation is especially useful after reading binary data to verify the data integrity:

.. code:: python

   import steel
   from io import BytesIO
   from steel.fields.base import ValidationError

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   # Read potentially corrupted data
   binary_data = some_binary_source()
   buffer = BytesIO(binary_data)

   try:
       packet = NetworkPacket.read(buffer)
       packet.validate()  # Verify the parsed data is valid
       print("Data successfully validated")
   except ValidationError as e:
       print(f"Corrupted data detected: {e}")

Best Practices
==============

#. **Validate after reading**: Always validate structures after reading from external sources to
   catch data corruption early.
#. **Validate before writing**: Call validate() before writing to ensure complete, valid data.
#. **Handle missing fields**: Use try/except blocks to gracefully handle incomplete structures.
#. **Validate incrementally**: For complex structures, consider validating fields as you set them
   rather than waiting until the end.

.. code:: python

   import steel
   from steel.fields.base import ValidationError

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   # Good practice: validate after reading unknown data
   def parse_file(filepath):
       with open(filepath, 'rb') as f:
           try:
               packet = NetworkPacket.read(f)
               packet.validate()
               return packet
           except ValidationError:
               raise ValueError(f"Invalid file format: {filepath}")

   # Good practice: ensure completeness before writing
   def write_packet(packet, output):
       packet.validate()  # Ensures all fields are present and valid
       return packet.write(output)

****************
 Advanced Usage
****************

Configuring all the fields in a structure
=========================================

Structures can be configured with global options that affect all fields on that structure.

.. code:: python

   import steel

   class NetworkPacket(steel.Structure, endianness=">", encoding="ascii"):
       header = steel.Integer(size=2)  # Will encode big-endian values
       message = steel.NullTerminatedString()  # Will use ASCII encoding
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

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   # Access all fields
   for name, field in NetworkPacket._config.fields.items():
       print(f"Field {name}: {field.__class__.__name__}")

   # Access specific field
   header_field = NetworkPacket._config["header"]
   print(f"Header field size: {header_field.size}")

This configuration option has the following attributes:

   -  ``fields`` is a dictionary of the fields that are specified on the structure. Because Python
      dictionaries are ordered by default, iterating over this dictionary -- or its keys or values
      individually -- will yield fields in the correct order.

   -  ``options`` is a dictionary of field options that were supplied at the structure level. This
      will contain everything that was supplied in the class definition, regardless of whether it
      actually overrode any pariticular field's configuration.
