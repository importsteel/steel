#################
 Getting Started
#################

Steel makes binary data parsing type-safe and intuitive. This guide will walk you through the
basics.

**************
 Installation
**************

Install Steel using pip:

.. code:: bash

   pip install steel

***************
 Core Concepts
***************

Steel consists of two main features: structures and fields.

-  *Structures* are collections of fields, in a specific order. They build up the overall format of
   the data, and provide utilities for reading, writing and validating data as a whole. Example
   structures could be the PNG image format, and also just the header chunk from the PNG image
   format.

-  *Fields* are the building blocks of Steel structures. They define how data is encoded, decoded,
   and validated. Some examples are `Integer`, `String` and `Flags`. Fields can reference other
   fields or even other structures.

*************
 Basic Usage
*************

Consider popular GIF image files. They contain a lot of information, including metadata, color
palettes and compressed pixel data, possibly with multiple frames of animation. To keep things
simple, let's just start by getting the width and height of the image.

Define a structure
==================

.. code:: python

   class GifVersion(StrEnum):
      GIF_87a = '87a',
      GIF_89a = '89a',

   class GifVersion(steel.StringEnum):
      inner_field = steel.FixedLengthString(size=3, encoding='ascii')
      enum_class = GifVersion

   class GIF(steel.Structure):
      magic = steel.FixedBytes(b'GIF')
      version = GifVersion()
      width = steel.Integer(size=2, endianness=steel.ByteOrder.LITTLE_ENDIAN)
      height = steel.Integer(size=2, endianness=steel.ByteOrder.LITTLE_ENDIAN)

   class FileHeader(steel.Structure):
      magic = steel.String(size=4)          # 4-byte magic number
      version = steel.Integer(size=2)       # 2-byte version
      flags = steel.Integer(size=2)         # 2-byte flags
      file_size = steel.Integer(size=4)     # 4-byte file size
      timestamp = steel.Timestamp(size=8)   # 8-byte timestamp

This touches on a few differet features right away, so let's break it down. First, we import Steel.

.. code:: python
   import steel

One of the early fields in the format is a version identifer, so we create a simple custom field to interpret that version.

.. code:: python

   class GifVersion(StrEnum):
      GIF_87a = '87a',
      GIF_89a = '89a',

   class GifVersion(steel.StringEnum):
      inner_field = steel.FixedLengthString(size=3, encoding='ascii')
      enum_class = GifVersion


Read Binary Data
================

.. code:: python

   # Read from a file
   with open('data.bin', 'rb') as f:
      header = FileHeader.read(f)

   # Read from bytes
   data = b'\x50\x4b\x03\x04\x14\x00\x00\x00\x00\x01\x02\x03\x04\x00\x00\x00\x00\x00\x00\x00'
   header = FileHeader.unpack(data)

   # Access fields with full type safety
   print(f"Magic: {header.magic}")      # Type: str
   print(f"Version: {header.version}")  # Type: int
   print(f"Size: {header.file_size}")   # Type: int

Write Binary Data
=================

.. code:: python

   # Create a structure instance
   header = FileHeader()
   header.magic = "STLF"
   header.version = 1
   header.flags = 0
   header.file_size = 1024
   header.timestamp = time.time()

   # Write to a file
   with open('output.bin', 'wb') as f:
      header.write(f)

   # Or get bytes
   data = header.pack()

*************
 Field Types
*************

Steel provides several built-in field types:

Numbers
=======

.. code:: python

   from steel.fields import Integer, Float

   class Numbers(Structure):
      byte_val = Integer(size=1)      # 1-byte integer
      short_val = Integer(size=2)     # 2-byte integer
      int_val = Integer(size=4)       # 4-byte integer
      long_val = Integer(size=8)      # 8-byte integer

      float_val = Float(size=4)       # 4-byte float
      double_val = Float(size=8)      # 8-byte double

Strings
=======

.. code:: python

   from steel.fields import String

   class Strings(Structure):
      fixed_str = String(size=10)     # Fixed-size string
      # More string types available - see documentation

Enums
=====

.. code:: python

   from enum import IntEnum
   from steel.fields import IntegerEnum

   class FileType(IntEnum):
      TEXT = 1
      BINARY = 2
      COMPRESSED = 3

   class Header(Structure):
      file_type = IntegerEnum(FileType)

Datetime
========

.. code:: python

   from steel.fields import Timestamp, Duration

   class TimeData(Structure):
      created_at = Timestamp()        # Unix timestamp -> datetime
      duration = Duration()           # Seconds -> timedelta

*************
 Type Safety
*************

Steel provides full type safety with modern Python:

.. code:: python

   # Your IDE will know the exact types
   header = FileHeader.read(file)
   header.magic      # Type: str
   header.version    # Type: int
   header.timestamp  # Type: float

   # Type errors are caught at static analysis time
   header.version = "not a number"  # mypy/pylance error!

************
 Next Steps
************

-  [**Documentation**]({{ site.docs_url }}) - Complete API reference
-  [**Examples**]({{ site.github.repository_url }}/tree/main/examples) - Real-world usage examples

************
 Need Help?
************

-  [GitHub Issues]({{ site.github.repository_url }}/issues) - Report bugs or ask questions
-  [Documentation]({{ site.docs_url }}) - Comprehensive guides and API reference

# Steel Features

Steel brings modern Python practices to binary data parsing with comprehensive type safety and
extensibility.

*************
 Type Safety
*************

Full Generic Support
====================

.. code:: python

   from steel.fields import Field, Integer
   from steel.structure import Structure

   class MyField(Field[int]):
      # Full type hints throughout
      def validate(self, value: int) -> None: ...
      def pack(self, value: int) -> bytes: ...
      def unpack(self, data: bytes) -> int: ...

   class MyStructure(Structure):
      value: int = MyField()  # IDE knows this is int

Runtime Validation
==================

.. code:: python

   field = Integer(size=1)
   field.validate(42)   # OK
   field.validate(300)  # ValidationError

******************
 Rich Field Types
******************

Numeric Fields
==============

.. code:: python

   from steel.fields import Integer, Float

   class Data(Structure):
      # Integers with configurable size and endianness
      small = Integer(size=1)           # 1-byte
      big_endian = Integer(size=4, endian='big')

      # Floating point
      float32 = Float(size=4)
      float64 = Float(size=8)

String Fields
=============

.. code:: python

   from steel.fields import String

   class TextData(Structure):
      fixed = String(size=10)           # Fixed-size string
      # Additional string types in full documentation

Enum Fields
===========

.. code:: python

   from enum import IntEnum, StrEnum
   from steel.fields import IntegerEnum, StringEnum

   class Status(IntEnum):
      INACTIVE = 0
      ACTIVE = 1

   class Protocol(StrEnum):
      HTTP = "http"
      HTTPS = "https"

   class Config(Structure):
      status = IntegerEnum(Status)
      protocol = StringEnum(Protocol)

Date and Time
=============

.. code:: python

   from steel.fields import Timestamp, Duration
   from datetime import datetime, timedelta

   class LogEntry(Structure):
      timestamp = Timestamp()           # int -> datetime
      duration = Duration()             # float -> timedelta

   # Usage
   entry = LogEntry.read(file)
   print(entry.timestamp)  # datetime object
   print(entry.duration)   # timedelta object

***************
 Extensibility
***************

Custom Fields
=============

Create your own field types easily:

.. code:: python

   from steel.fields import Field

   class IPv4Address(Field[str]):
      def validate(self, value: str) -> None:
         # Validate IP address format
         pass

      def pack(self, value: str) -> bytes:
         # Convert "192.168.1.1" to 4 bytes
         parts = [int(p) for p in value.split('.')]
         return bytes(parts)

      def unpack(self, data: bytes) -> str:
         # Convert 4 bytes to "192.168.1.1"
         return '.'.join(str(b) for b in data)

Wrapped Fields
==============

Transform existing fields to new types:

.. code:: python

   from steel.fields import WrappedField, Integer
   from datetime import datetime

   class Timestamp(WrappedField[datetime, int]):
      inner_field = Integer(size=4)

      def wrap(self, timestamp: int) -> datetime:
         return datetime.fromtimestamp(timestamp)

      def unwrap(self, dt: datetime) -> int:
         return int(dt.timestamp())

*******************
 Advanced Features
*******************

Conditional Fields
==================

.. code:: python

   # Fields that depend on other field values
   class Packet(Structure):
      packet_type = Integer(size=1)
      # Conditional fields based on packet_type
      # See documentation for full conditional field support

Nested Structures
=================

.. code:: python

   class Point(Structure):
      x = Float(size=4)
      y = Float(size=4)

   class Rectangle(Structure):
      top_left = Point
      bottom_right = Point

****************
 Error Handling
****************

Comprehensive Error Types
=========================

.. code:: python

   from steel.fields import ValidationError, ConfigurationError

   try:
      data = SomeStructure.read(file)
   except ValidationError as e:
      print(f"Invalid data: {e}")
   except ConfigurationError as e:
      print(f"Field misconfigured: {e}")

Detailed Error Messages
=======================

Steel provides clear, actionable error messages for debugging binary format issues.

************
 Next Steps
************

-  [**Documentation**]({{ site.docs_url }}) - Complete API reference
-  [**GitHub**]({{ site.github.repository_url }}) - Source code and examples
