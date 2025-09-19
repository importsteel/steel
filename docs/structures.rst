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

Use the ``load()`` class method to parse binary data:

.. code:: python

   import steel
   from io import BytesIO

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   binary_data = b"\xd2\x04Hello\x00\xcd\xab"
   buffer = BytesIO(binary_data)
   packet = NetworkPacket.load(buffer)

   print(packet.header)    # 1234
   print(packet.message)   # "Hello"
   print(packet.checksum)  # 0xABCD

If you don't have (or want) a file-like object, you can also use ``loads()`` to read from a sequence
of ``bytes`` instead.

.. code:: python

   packet = NetworkPacket.loads(binary_data)

   print(packet.header)    # 1234
   print(packet.message)   # "Hello"
   print(packet.checksum)  # 0xABCD

Writing to Buffers
==================

Use the ``dump()`` method to serialize data back to binary format:

.. code:: python

   packet = NetworkPacket(header=1234, message="Hello", checksum=0xABCD)

   output = BytesIO()
   bytes_written = packet.dump(output)

   binary_data = output.getvalue()
   print(f"Wrote {bytes_written} bytes")

If you don't have (or want) a file-like object, you can also use ``dumps()`` to return a sequence of
``bytes`` instead.

.. code:: python

   binary_data = packet.dumps()
   print(f"Wrote {len(binary_data)} bytes")

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

.. important::

   Validation is _not_ performed automatically. Many projects don't need it, and many more don't
   need it to happen every time a structure is written out, so it's a separate step. For cases that
   do need it, validation is sipmle to perform, so this shouldn't be too onerous a requirement.

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

The validation process checks that each field has a value and is valid, according to its specific
constraints. See the documentation for each field for details on its validation behavior.

Handling Validation Errors
==========================

When validation fails, a ``ValidationError`` is raised with details about the problem:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   packet = NetworkPacket(header=70000, message="Hello", checksum=0xABCD)  # Header too big

   try:
       packet.validate()
   except steel.ValidationError as e:
       print(f"Validation failed: {e}")

Common validation scenarios that raise errors:

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   packet = NetworkPacket(header=70000, message="Hello", checksum=0xABCD)
   packet.validate()  # ValidationError: value exceeds maximum

   packet = NetworkPacket(header=1234, message="héllo", checksum=0xABCD)
   packet.validate()  # ValidationError: invalid encoding

.. note::

   If multiple fields are invalid, _one_ `ValidationError` will be raised, for the field field that
   failed to validate. A future update may include an API to retrieve multiple validation errors in
   one pass.

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

Validation is also useful after reading binary data to verify the data integrity:

.. code:: python

   import steel
   from io import BytesIO

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   # Read potentially corrupted data
   binary_data = some_binary_source()
   buffer = BytesIO(binary_data)

   try:
       packet = NetworkPacket.load(buffer)
       packet.validate()  # Verify the parsed data is valid
       print("Data successfully validated")
   except steel.ValidationError as e:
       print(f"Corrupted data detected: {e}")

.. warning::

   This approach only works if all the fields can at least read the data into the structure. If any
   field fails to even get that far (such as invalid text for a specified encoding), field-specific
   exceptions can be raised during `load()`, so you should prepare for that as well.

Best Practices
==============

#. **Validate before writing**: Call ``validate()`` before writing to ensure complete, valid data.
#. **Handle missing fields**: Use try/except blocks to gracefully handle incomplete structures.
#. **Validate incrementally**: For complex structures, consider validating fields as you set them
   rather than waiting until the end.
#. **Validate after reading**: Always validate structures after reading from external sources to
   catch data corruption early.
#. **Prepare for exceptions during reading**: Don't assume that every file can be read well enough
   to be able to call ``validate()`` on the result.

.. code:: python

   import steel

   class NetworkPacket(steel.Structure):
       header = steel.Integer(size=2)
       message = steel.NullTerminatedString(encoding="ascii")
       checksum = steel.Integer(size=2)

   # Good practice: validate after reading unknown data
   def parse_file(filepath):
       with open(filepath, "rb") as f:
           try:
               packet = NetworkPacket.load(f)
               packet.validate()
               return packet
           except steel.ValidationError:
               raise ValueError(f"Invalid file format: {filepath}")

   # Good practice: ensure completeness before writing
   def write_packet(packet, output):
       packet.validate()  # Ensures all fields are present and valid
       return packet.write(output)

****************
 Advanced Usage
****************

Configuring fields at the structure level
=========================================

Structures can contain many fields with similar configuration options, such as byte ordering or text
encoding. You can configure each of these fields individually, but to simplify the structure
definition, you may also configure these options at the structure level. Structures can be
configured with global options that affect all fields on that structure. In addition to supplying
`steel.Structure` as a base class, you can specify many options as keyword arguments when defining
the class.

.. code:: python

   import steel

   class NetworkPacket(steel.Structure, endianness=">", encoding="ascii"):
       header = steel.Integer(size=2)  # Will encode big-endian values
       message = steel.NullTerminatedString()  # Will use ASCII encoding
       checksum = steel.Integer(size=4, endianness="<")  # Overrides to little-endian

.. note::

   Option specified on the structure will override any defaults defined in the fields, but
   configuring individual fields will take priority over anything specified on the structure.

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
