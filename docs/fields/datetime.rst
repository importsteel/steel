##################
 Date/Time Fields
##################

Handle date, time, and duration values stored in binary formats. These fields convert between
Python's ``datetime`` objects and their binary representations.

***********
 Timestamp
***********

The ``Timestamp`` field stores ``datetime`` objects as POSIX timestamps (seconds since midnight UTC
on January 1, 1970). It automatically converts between Python ``datetime`` objects and integer
timestamps.

.. code:: python

   created_at = steel.Timestamp()
   modified_at = steel.Timestamp(timezone=ZoneInfo("America/New_York"))

Parameters
==========

-  **timezone**: Timezone to use when converting timestamps to datetime objects (default: UTC). Must
   be a ``ZoneInfo`` object. All ``datetime`` objects produced by this field will have this
   timestamp attached to them, so that conversions can be done properly. *Can be specified at the
   structure level.*

.. warning::

   This field uses its ``timezone`` attribute to automatically convert the timestamp to UTC before
   writing out the data, and it assumes all input is in UTC. If you need to read or write data in a
   local timezone instead of UTC, consider writing a :doc:`custom field <custom-fields>`.

Example Usage
=============

.. code:: python

   from datetime import datetime
   from zoneinfo import ZoneInfo

   import steel

   class LogEntry(steel.Structure):
       timestamp = steel.Timestamp(timezone=ZoneInfo("UTC"))
       level = steel.Integer(size=1)

   # Create with current time
   entry = LogEntry(timestamp=datetime.now(), level=1)

   buffer = BytesIO()
   entry.write(buffer)

Naive ``datetime`` objects
==========================

```datetime``` objects can be created without specifying a timezone, which are considered to be
"naive". These can introduce uncertainty when converting to explicit timezones elsewhere. Python's
own behavior is to use the system's local timezone for timezone-aware operations, under the
assumption that the time in the object is valid for the computer running the code.

Steel doesn't need to make that assumption, because a timezone is always configured into the
``Timestamp`` field itself. So any naive ``datetime`` objects that are supplied for this field will
automatically have the field's timezone applied to them before converting to UTC during the writing
process.

.. important::

   Just to be very clear, Steel's behavior for naive ``datetime`` objects differs from Python's own
   behavior. Steel has access to more information and can be more consistent. If your programs are
   relying on an implicit local timezone, it's best to either specify that same timezone on all of
   your ``Timestamp`` fields or add it to your ``datetime`` objects directly, making them
   timezone-aware.

**********
 Duration
**********

The ``Duration`` field handles lengths of time as a number of seconds. Because Python's `timedelta`
objects include fractional seconds, ``Duration`` fields store their values using a 4-byte
``FloatField`` internally.

.. code:: python

   timeout = steel.Duration()
   interval = steel.Duration()

.. note::

   Any use of floating-point values has a possibility of losing a small amount of precision. Even
   though ``Duration`` doesn't directly do any mathematical calculations that would affect the
   precision of the provided value, a roundtrip conversion from Python to a file and back can result
   in a slightly different value. This is simply part of the nature of working with floating-point
   numbers.

Example Usage
=============

.. code:: python

   from datetime import timedelta
   import steel

   class TaskConfig(steel.Structure):
       timeout = steel.Duration()
       retry_interval = steel.Duration()

   config = TaskConfig(
       timeout=timedelta(minutes=5),
       retry_interval=timedelta(seconds=2.5),
   )
