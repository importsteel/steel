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

Structures
==========

Structures are collections of fields, in a specific order. They build up the overall format of the
data, and provide utilities for reading, writing and validating data as a whole. Example structures
could be the entire PNG image format, or perhaps just the header chunk from the PNG image format.

.. warning::

   By calling them structures, it's easy to try to think of them in the same way as the `struct`
   paradigm in C. While there are undoubtedly some similarities, Steel was not designed to resemble
   C, so any such similarities are coincidental. Looking at Steel through the lens of experience
   with C will likely lead to confusion.

Fields
======

Fields are the building blocks of Steel structures. They define how data is encoded, decoded, and
validated. Some examples are `Integer`, `String` and `Flags`. Fields can reference other fields or
even other structures.

*************
 Basic Usage
*************

Consider popular GIF image files. They contain a lot of information, including metadata, color
palettes and compressed pixel data, possibly with multiple frames of animation. To keep things
simple, let's just start by getting the width and height of the image.

Define a structure
==================

Let's start by getting the dimensions of a GIF image. These files start with "GIF" to identify the
file type and a version number to determine the layout of the file, followed immediately by the
width and height, in all versions.

.. code:: python

   import steel

   class GIF(steel.Structure):
      magic = steel.FixedBytes(b'GIF')
      version = steel.FixedLengthString(size=3)
      width = steel.Integer(size=2)
      height = steel.Integer(size=2)

Read Data
=========

.. code:: python

   with open('logo.gif', 'rb') as f:
      image = GIF.read(f)

   print(f"Version: {image.version}")
   print(f"Size: {image.width}x{image.height}")

Write Data
==========

.. code:: python

   # Create an instance of the GIF structure
   image = GIF(version='89a', width=125, height=125)

   with open('header.gif', 'wb') as f:
      image.write(f)

************
 Learn More
************

Now that you know the basics, you can read more about :doc:`structures` and :doc:`fields` in their
own documentation.
