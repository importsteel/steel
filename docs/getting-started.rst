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
   print(f"Version: {header.version}")
   print(f"Size: {header.width}x{header.height}")

Write Data
==========

.. code:: python

   # Create an instance of the GIF structure
   image = GIF(version='89a', width=125, height=125)

   with open('header.gif', 'wb') as f:
      image.write(f)
