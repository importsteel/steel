#######################
 Writing custom fields
#######################

Steel provides fields for interacting with a wide range of common data formats, but there will
always be more in the wild than any framework could hope to cover. For those custom cases, or where
you want to customize the behavior of the framework, you can create your own custom fields.

*****************
 Field Structure
*****************

Fields are simply Python classes, with a few specific characteristics:

   -  Subclass from a common ancestor
   -  A set of common methods and properties

Subclassing ``Field[T]``
========================

The base field class is ``steel.fields.base.Field``. This is a generic type, which uses a parameter
to describe the native Python type it handles. So a data field to manage strings would subclass
``Field[str]``, while a field to store timestmaps would use ``Field[datetime]``. Throughout the
remainder of these docs, this generic type paraemter will be referred to as ``T``.

Existing fields already subclass the appropriate type, so sublcassing any of them will share the
same type hinting as its parent class.

.. note::

   Python projects are well-known for their use of "duck typing", where they can use any object
   type, as long as it provides the right API. In order to more easily identify fields from other
   attributes, and to make type hinting more consistent, Steel does in fact require the use of the
   ``Field`` base class for all fields.

API Methods
===========

There are five key methods that all fields are expected to provide. Their definitions here include
the type information they're expected to convey as well.

``validate(value: T) -> None``
------------------------------

Validates that a value is suitable for this field, according to its type and configuration. It miust
returns ``None`` when the provided value is valid for storage, and it should instead raise
``ValidationError`` if there's anything wrong with it. The message in the exception should describe
what's wrong, so that it can be reported elsewhere.

This is a helper method, which is expected to be called by separate validation tooling or user
interfaces. It is __not__ called at any point during reading or writing data. So if you want to use
to ensure data integrity, be sure to call it yourself separately.

``read(buffer: BufferedIOBase) -> tuple[T, int]``
-------------------------------------------------

Reads data from a data buffer, such as a file, and returns a fully-unpacked value as well the number
of bytes consumed from the buffer.

Not all data structures have a size that can be known up front, so this method can adjust the read
length as necessary, based on any combination of the field and the actual data that was found.
Returning the number of bytes alongside the Python value provides visibility into this behavior.

This method is also responsible for the unpacking step below. Most implementations will read the
appropriate number of bytes and pass them along to the ``pack()`` method to get a Python value to
return. But some fields may already be fully unpacked as part of the process of reading data from
the file. In these cases, there's no need to call ``pack()`` as a separate step, and ``read()`` can
simply return the appropriate value directly.

.. important::

   This is defined an abstract method, so unless you're subclassing an existing discrete field, you
   will need to provide an implementation of this method.

``unpack(value: bytes) -> T``
-----------------------------

Converts a sequence of bytes into a native Python object. The bytes provided will have already been
read from the buffer, this method simply provides a convenient way to modify how those bytes are
interpreted. In most cases, this will simply perform the inverse of the ``pack()`` method.

.. important::

   This is defined an abstract method, so unless you're subclassing an existing discrete field, you
   will need to provide an implementation of this method.

   If your implementation of the ``read()`` method returns a native value without the need for an
   encoding step, this method must still exist, and can simply contain ``pass``.

``pack(value: T) -> bytes``
---------------------------

Encodes a native Python object into a sequence of bytes, suitable for writing to the data buffer. In
most cases, this will simply perform the inverse of the ``unpack()`` method.

.. important::

   This is defined an abstract method, so unless you're subclassing an existing discrete field, you
   will need to provide an implementation of this method.

   If your implementation of the ``write()`` method can write out data without the need for an
   unpacking step, this method must still exist, and can simply contain ``pass``.

``write(self, value: T, buffer: BufferedIOBase) -> int``
--------------------------------------------------------

Writes out a fully-packed byte sequence representing a native Python object. Like ``read()``, this
returns the number of bytes that were written to the buffer.

In most cases, there's no need to override this method with a custom implementation. The ``pack()``
method already returns a sequence of bytes suitable for writing, and the number of bytes to write
can be determined by the length of that sequence.

.. tip::

   This method is __not__ defined as abstract, and most fields can safely rely on the base
   implementation, which simply writes all the bytes returned by the ``pack()`` method.

****************
 Helper Classes
****************

``ExplicitlySizedField[T]``
===========================

A specific form of ``Field`` base class that adds a ``size`` attribute. With a fixed size as part of
the field's configuration, this class provides a default ``read()`` implementation that reads
exactly ``self.size`` bytes and passes the result straight to the ``unpack()`` method.

``ConversionField[T, D]``
=========================

Subclassing an existing field can provide further customization, but the subclass must still use the
same native Python type, such as all the `int` fields above. Sometimes you may want to use an
existing field to interact with the data buffer but interact with Python using a different type. One
example used within Steel is the ``Timestamp`` field, which stores data using an ``Integer`` field
internally, but presents a `datetime` object to external code.

``ConversionField`` expands on the existing ``Field`` base class to specify two distinct data types.
``T`` works like any other field, specifying the data type that consumers of this field will
interact with. The extra ``D`` refers to the type of the underlying conversion field. The actual
interaction with the data buffer will be handled by a field supplied as an ``inner_field`` class
attribute.

In the timestamp example, ``T`` would be ``datetime``, while ``D`` would be ``int``. This handles
the necessary type hinting, and an ``Integer`` field would handle the interactions in code. All
that's left is to convert between ``datetime`` and ``int``.

.. code:: python

   class Timestamp(ConversionField[datetime, int]):
       inner_field = Integer(size=4)

       def to_data(self, value: datetime) -> int:
           return int(value.timestamp())

       def to_python(self, value: int) -> datetime:
           return datetime.fromtimestamp(value)

.. warning::

   Don't use this ``Timestamp`` field. It's here for a useful demonstration, but the actual
   implementation has more features and has a stable API.

*************
 Error Types
*************

Steel provides two main exception types for field operations:

``ConfigurationError``
======================

Raised during field initialization when configuration is invalid. Use this when:

-  Invalid parameters are passed to field constructors
-  Incompatible options are specified together

``ValidationError``
===================

Raised when a value fails validation. Use this when:

-  Values are out of range
-  Required format constraints aren't met
-  Data cannot be properly encoded

****************
 Best practices
****************

#. **Only read what you need**: Be conservative when reading from the data buffer. Consuming more
   data than is required by the field can cause problems with other fields that need to continue
   reading after your field is finished. It's also important to minimize reads on potentially large
   files, to keep memory usage as low as possible.

#. **Account for partial reads**: When implementing ``read()``, account for the possibility that the
   data is incomplete. If a file gets truncated, or if certain structures are corrupted, a read may
   not return as much as you would expect. Some data, like strings, may be able to handle this
   gracefully, but most will have to raise an informative exception instead.

   .. code:: python

      data = buffer.read(expected_size)
      if len(data) < expected_size:
          raise ValueError(
              f"Unexpected end of buffer: got {len(data)}, expected {expected_size}"
          )

#. **Use configuration defaults sparingly**: It can be tempting to provide defaults for
   configuration options that seem to the obvious choice, but in practice it may not be as obvious
   as it seems. Defaults can obscure those differences, leading users to accidentally depend on a
   configuration that's unsuitable for their needs. Here are some examples:

   -  x86 systems use little-endian byte ordering internally, and many applications will simply copy
      data structures from memory to files, preserving that ordering. But there are plenty of other
      systems with other needs, so defaulting to little-endian could make it harder for users to
      realize they should be making a conscious choice here.

   -  Strings in C are null-terminated, which again is often written directly to files as a matter
      of convenience. But data written for other systems that don't use C may use other formats,
      such as storing a string's length __before__ the text, or may allocate a fixed number of bytes
      for strings, regardless of how many bytes are actually populated. Steel provides three
      different field types for these cases.
