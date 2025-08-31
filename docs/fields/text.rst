#############
 Text Fields
#############

Read and write Unicode text with configurable character encodings and
other considerations. Strings can come in varying lengths, which can be
stored in a few different ways, so there are multiple text fields to
handle different behaviors.

************
 Shared API
************

All text fields share a common API that's independent of how the bytes
are arranged.

Parameters
==========

-  **encoding**: Character encoding to use (e.g., 'utf-8', 'ascii',
   'latin-1'). These match Python's native encodings, and there is no
   default.

Character vs Byte Length
========================

Most of the following fields also have a ``size`` parameter, which, like
all other fields, refers to the number of bytes that are used to encode
the value in a data stream. For many text encodings and termination
styles, this can be very different from the number of characters in the
decoded string.

.. code:: python

   field = FixedLengthString(size=5, encoding="utf-8")

   # ASCII: 1 byte per character
   field.pack("hello")  # b'hello' (5 bytes, which can be stored successfully)

   # UTF-8: Variable bytes per character
   field.pack("héllo")  # b'h\xc3\xa9llo' (6 bytes, which would exceed the size limit)

*******************
 FixedLengthString
*******************

Strings that are always stored in a pre-defined amount of bytes,
regardless of the length of the string. The returned value can never be
longer than the size of the field, but it can be smaller.

Additional Parameters
=====================

-  **size**: Maximum size in bytes for the string data.

-  **padding**: Byte to use to pad shorter strings to fit the full
   length of the field. When reading from a data stream, this padding
   will automatically be stripped out, and when writing to a stream, it
   will be added as necessary. (default: ``b'\x00'``)

.. code:: python

   FixedLengthString(size=20, encoding="ascii")

********************
 LenghIndexedString
********************

Strings where the length is stored as a separate field before the string
data itself. This is commonly known as a Pascal string format, where a
length prefix indicates how many bytes follow for the actual string
content.

Additional Parameters
=====================

-  **size**: A field representing the size of the string to read. To
   allow for that size to be stored in different ways, this can be any
   field that yields a Python `int`. For example, a 2-byte length prefix
   can be accessed with an ``Integer(size=2)`` field.

.. code:: python

   from steel import Integer

   LenghIndexedString(size=Integer(size=2), encoding="utf-8")

.. tip::

   ``PascalString`` is provided an alias for ``LenghIndexedString``, for
   authors more familiar with that name.

******************
 TerminatedString
******************

Strings that are terminated by a specific value, rather than having a
predetermined length. The string continues until the terminator byte is
encountered in the data stream.

.. code:: python

   TerminatedString(encoding="ascii")

Additional Parameters
=====================

-  **terminator**: Byte sequence that marks the end of the string data.
   (default: ``b'\x00'``)

The terminator must be exactly one byte long. When reading, the
terminator byte is consumed from the stream but not included in the
returned string value. When writing, the terminator is automatically
appended to the encoded string data.

Example Usage
=============

.. code:: python

   TerminatedString(encoding="ascii", terminator=b";")

.. tip::

   ``CString`` is provided an alias for ``TerminatedString``, for
   authors more familiar with that name.
