########
 Fields
########

Fields are named components within a structure. At their most basic, they represent simple values
that can be converted directly to Python primitives, like ``int`` and ``str``. More complex fields
could contain multiple attributes, value lists or nested structures.

**************
 Using Fields
**************

Fields are assigned as attributes to a :doc:`Structure <structures>`'s class definition. This
assignment allows for naming individual fields, as well as configuring each field as necessary:

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

Field are added from top to bottom, in the order that the data appears in the target data structure.
So a data stream for the ``Header`` above could look like this:

.. code:: python

   data = (
       b"DATA"  # tag
       b"\x01"  # major_version
       b"\x05"  # minor_version
       b"OW\xb0h"  # created_date
       b"Example\x00"  # title
   )
   # Resulting value: b'DATA\x01\x05OW\xb0hExample\x00'

After loading the structure, fields can be accessed as instance attributes, which will present the
data in native data types defined by each field:

.. code:: python

   obj = Header.loads(data)
   (
       obj.tag,          # DATA
       obj.version,      # 1.5
       obj.created_date  # datetime.datetime(2025, 8, 28, 9, 19, 11)
       obj.title         # 'Example'

   )

************
 Shared API
************

All fields contain a shared set of attributes and methods, which are used as a high-level API for
interacting with all types of data. Most field methods will interact with a native Python data type
that's dependent on the field being used. In these descriptions, ``T`` is used to represent this
native type.

``validate(value: T) -> None``
==============================

Checks that the supplied value is valid, according to the rules specified by the field and its
configuration. This method has no distinct return value because an invalid value will raise an
exception with details about the problems with the supplied value. If it returns without exception,
the value can be considered valid.

``read(stream: BufferedIOBase) -> tuple[T, int]``
=================================================

Reads the appropriate number of bytes from a data stream, such as a file, and returns a 2-tuple with
the resulting value and the number of bytes that were read.

.. code:: python

   title = steel.FixedLengthString(size=10, encoding="ascii")
   stream = BytesIO(b"Example\x00\x00\x00")

   title.read(stream)  # ('Example', 10)

``pack(value: T) -> bytes``
===========================

Converts a native Python value to ``bytes``. The input value for this method will depend on the
field being used. Check the field documentation for more details.

``unpack(value: bytes) -> T``
=============================

Converts ``bytes`` from the data stream to a native Python object. The return type of this method
will depend on the field being used. Check the field documentation for more details.

``write(value: T, stream: BufferedIOBase) -> int``
==================================================

Writes the appropriate bytes to a data stream, such as a file, and returns the number of bytes that
were written.

.. code:: python

   title = steel.FixedLengthString(size=10, encoding="ascii")
   stream = BytesIO(b"Example\x00\x00\x00")

   title.write("Example", stream)  # 10
   stream.getvalue()  # b'Example\x00\x00\x00'

*************
 Field Types
*************

Steel provides fields in various categories, with detailed documentation for each:

.. toctree::
   :maxdepth: 2

   fields/numbers
   fields/text
   fields/bytes

And custom fields can be added as well:

.. toctree::
   :maxdepth: 2

   fields/custom-fields
