#############
 Enum Fields
#############

Many data structures have fields with pre-defined values, with specific meanings beyond what's found
in the data itself. Format specifiers, value types and flags are just a few of the options
available. Python provides an ``enum`` module to work with this type of value, and Steel can
translate between those and your underlying data.

.. note::

   Python provides a generic ``Enum`` type that doesn't restrict its values to any particular data
   type. This isn't suitable for Steel, which needs to know how to consistently convert those values
   to and from a sequence of ``bytes``. So Steel doesn't have any support for bare ``Enum`` types.

*****************
 Overall process
*****************

All of Steel's ``enum``-related fields work in a similar way. Designate an ``enum`` type with the
values you want to work with, in the appropriate type for the data that will hold those values, and
pass that ``enum`` in as the first argument to the appropriate field type. Unlike most field
arguments, the ``enum`` can be supplied as a positional argument and is always required.

*************
 IntegerEnum
*************

The ``IntegerEnum`` field pairs with Python's ``IntEnum`` class to read and write values as
integers.

.. code:: python

   from enum import IntEnum

   import steel

   class Priority(IntEnum):
       LOW = 1
       MEDIUM = 2
       HIGH = 3

   class Task(steel.Structure):
       priority = steel.IntegerEnum(Priority)

Parameters
==========

-  **enum_class**: The ``IntEnum`` subclass defining the valid values
-  **size**: Number of bytes for the underlying integer (default: 1)

The enum value is stored as an integer using the specified number of bytes. A matching
``IntegerField`` is instantiated internally to manage that portion of the interaction.

Example Usage
=============

.. code:: python

   from enum import IntEnum

   class Status(IntEnum):
       INACTIVE = 0
       ACTIVE = 1
       PENDING = 2
       DELETED = 3

   class UserRecord(steel.Structure):
       user_id = steel.Integer(size=4)
       status = steel.IntegerEnum(Status)

   record = UserRecord(user_id=123, status=Status.ACTIVE)

   # Or with integer value (automatically converted)
   record = UserRecord(user_id=123, status=1)  # Same as Status.ACTIVE

   print(record.status.name)   # "ACTIVE"
   print(record.status.value)  # 1

************
 StringEnum
************

The ``StringEnum`` field pairs with Python's ``StringEnum`` class to read and write values as
strings. Because there's no default way to handle strings, ``StringEnum`` can't be instantiated on
its own; it must be subclassed. The subclass can then specify the appropriate configuration as its
own attributes.

.. code:: python

   from enum import StrEnum

   import steel

   class FileType(StrEnum):
       TEXT = "txt"
       IMAGE = "img"
       DATA = "dat"

   class FileTypeField(steel.StringEnum):
       enum_class = FileType
       wrapped_field = steel.FixedLengthString(size=3, encoding="ascii")

Parameters
==========

Must be defined as class attributes when subclassing:

-  **enum_class**: The ``StrEnum`` subclass defining valid string values

-  **wrapped_field**: A string field that defines how the enum value is stored. If this is a fixed
   size, it should be large enough to store all of the values in the ``enum``, but this is not
   validated automatically.

Example Usage
=============

.. code:: python

   from enum import StrEnum

   class Protocol(StrEnum):
       HTTP = "HTTP"
       HTTPS = "HTTPS"
       FTP = "FTP"

   class ProtocolField(steel.StringEnum):
       enum_class = Protocol
       wrapped_field = steel.TerminatedString(encoding="ascii")

   class NetworkConfig(steel.Structure):
       protocol = ProtocolField()
       port = steel.Integer(size=2)

   config = NetworkConfig(protocol=Protocol.HTTPS, port=443)

   print(config.protocol.name)   # "HTTPS"
   print(config.protocol.value)  # "HTTPS"

*******
 Flags
*******

The ``Flags`` field works somewhat similarly to ``IntegerEnum`` but pairs with Python's ``Flag``
class instead, to read and write values as integers but interact with them in Python as values that
can be combined with bitwise operations.

.. code:: python

   from enum import Flag

   class Permission(Flag):
       READ = 1
       WRITE = 2
       EXECUTE = 4

   class FileEntry(steel.Structure):
       permissions = steel.Flags(Permission)

Parameters
==========

-  **enum_class**: The ``Flag`` subclass defining the available flags
-  **size**: Number of bytes for the underlying integer (default: 1)

Example Usage
=============

.. code:: python

   from enum import Flag, auto

   class FileAttribute(Flag):
       HIDDEN = auto()     # 1
       READONLY = auto()   # 2
       SYSTEM = auto()     # 4
       ARCHIVE = auto()    # 8

   class FileHeader(steel.Structure):
       name = steel.FixedLengthString(size=12, encoding="ascii")
       attributes = steel.Flags(FileAttribute)

   # Create with combined flags
   header = FileHeader(
       name="config.txt",
       attributes=FileAttribute.READONLY | FileAttribute.ARCHIVE
   )

   # Check individual flags
   if FileAttribute.READONLY in header.attributes:
       print("File is read-only")

   # Get all active flags
   active_flags = list(header.attributes)  # [FileAttribute.READONLY, FileAttribute.ARCHIVE]

***********************
 Validation and Errors
***********************

All enum fields validate that values belong to their respective enum classes:

.. code:: python

   from enum import IntEnum

   class Color(IntEnum):
       RED = 1
       GREEN = 2
       BLUE = 3

   class Pixel(steel.Structure):
       color = steel.IntegerEnum(Color)

   # Valid usage
   pixel = Pixel(color=Color.RED)      # Works
   pixel = Pixel(color=1)              # Works (converted to Color.RED)

   # Invalid usage - raises ValidationError
   try:
       pixel = Pixel(color=99)         # No enum member with value 99
   except steel.ValidationError as e:
       print(f"Invalid color: {e}")

****************
 Advanced Usage
****************

Custom Integer Sizes
====================

You can specify custom integer sizes for ``IntegerEnum`` and ``Flags`` fields:

.. code:: python

   class LargeStatus(IntEnum):
       STATUS_A = 1000
       STATUS_B = 2000
       STATUS_C = 65535

   class Record(steel.Structure):
       # Use 2 bytes to accommodate larger enum values
       status = steel.IntegerEnum(LargeStatus, size=2)
