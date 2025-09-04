#############
 Byte Fields
#############

This set of fields doesn't do any type conversion of the underlying data, instead leaving bytes as
bytes. Many data formats contain data that doesn't need to be converted to anything else in order to
be useful, so these fields provide a way to access this data without any additional conversion
overhead.

It may easier to see this at the beginning of a GIF image file.

.. code:: python

   class Image(steel.Structure):
       tag = steel.FixedBytes(b"GIF")
       version = steel.Bytes(size=3)


   stream = b"GIF89a"
   image = Image.loads(stream)

   image.tag  # b'GIF'
   image.version  # b'89a'

Both of these value could instead be converted to strings, but their value as Unicode values is
limited. By keeping them as bytes, they can still be used for validation of the file, and also
simple code branching based on version, without needing to worry about text encodings.

*******
 Bytes
*******

An arbitrary sequence of bytes to expect at the specified position within a data stream.

Additional parameters
=====================

-  **size**: The number of bytes to expect within a data stream.

************
 FixedBytes
************

A pre-determined sequence of bytes to expect at the specified position within a data stream.
Validation ensures that the bytes in the stream match what's expected, and this field will also
write out the appropriate bytes if not provided in a structure.

Additional parameters
=====================

-  **value**: The sequence of bytes to expect within a data stream. Unlike most field
   configurations, this argument can be supplied positionally.

Because the length of the value is constant, there's no need to provide a separate ``size``
argument.
