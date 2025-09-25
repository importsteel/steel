import tempfile
import unittest
from io import BytesIO

from steel.base import Structure
from steel.fields.bytes import Bytes, FixedBytes
from steel.fields.nested import Object, OffsetBuffer
from steel.fields.numbers import Integer
from steel.fields.text import TerminatedString

from .. import ReadTracker


class TestOffsetBuffer(unittest.TestCase):
    def test_bytes_access(self):
        buffer = OffsetBuffer(BytesIO())

        # These can do anything
        self.assertTrue(buffer.seekable())
        self.assertTrue(buffer.readable())
        self.assertTrue(buffer.writable())

    def test_file_reader(self):
        with tempfile.TemporaryFile("rb") as file:
            buffer = OffsetBuffer(file)
            self.assertTrue(buffer.seekable())
            self.assertTrue(buffer.readable())
            self.assertFalse(buffer.writable())

    def test_file_writer(self):
        with tempfile.TemporaryFile("wb") as file:
            buffer = OffsetBuffer(file)
            self.assertTrue(buffer.seekable())
            self.assertFalse(buffer.readable())
            self.assertTrue(buffer.writable())

    def test_offset_seeking(self):
        data = BytesIO(b"123456789abcdef")
        buffer = OffsetBuffer(data, offset=5)

        self.assertEqual(buffer.tell(), 0)
        self.assertEqual(data.tell(), 5)

        buffer.seek(5)

        self.assertEqual(buffer.tell(), 5)
        self.assertEqual(data.tell(), 10)

    def test_offset_reader(self):
        data = BytesIO(b"123456789abcdef")
        buffer = OffsetBuffer(data, offset=5)

        self.assertEqual(buffer.tell(), 0)
        self.assertEqual(buffer.read(2), b"67")

    def test_offset_writer(self):
        data = BytesIO(b"123456789abcdef")
        buffer = OffsetBuffer(data, offset=5)

        self.assertEqual(buffer.tell(), 0)
        buffer.write(b"__")

        self.assertEqual(data.getvalue(), b"12345__89abcdef")

    def test_automatic_offset(self):
        data = BytesIO(b"123456789abcdef")
        data.seek(10)
        buffer = OffsetBuffer(data)

        self.assertEqual(buffer.tell(), 0)
        self.assertEqual(data.tell(), 10)

        buffer.seek(5)

        self.assertEqual(buffer.tell(), 5)
        self.assertEqual(data.tell(), 15)


class Color(Structure):
    red = Integer(size=1)
    green = Integer(size=1)
    blue = Integer(size=1)


class Metadata(Structure):
    title = TerminatedString()
    major_version = Integer(size=1)
    minor_version = Integer(size=1)


class TestObjectField(unittest.TestCase):
    def test_simple_size(self):
        field = Object(Color)

        input = ReadTracker(b"\x33\x7f\xcc")

        size, cache = field.get_size(input)

        self.assertEqual(size, 3)
        self.assertIsInstance(cache, Color)

        self.assertEqual(input.bytes_read, 0)

    def test_variable_size(self):
        field = Object(Metadata)

        input = ReadTracker(b"Steel\x00\x01\x00")

        size, cache = field.get_size(input)

        self.assertEqual(size, 8)
        self.assertIsInstance(cache, Metadata)

        self.assertEqual(input.bytes_read, 6)


class TestNestedStaticObject(unittest.TestCase):
    def test_field_assignment(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)

    def test_offset_chain(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)

        self.assertEqual(Swatch._config.offsets["version"], [0])
        self.assertEqual(Swatch._config.offsets["color"], [4])

    def test_greedy_loading(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)

        input = BytesIO(b"\x05\x00\x00\x00\x33\x7f\xcc")
        swatch = Swatch.load(input)

        self.assertEqual(swatch.version, 5)
        self.assertIsInstance(swatch.color, Color)
        self.assertEqual(swatch.color.red, 0x33)
        self.assertEqual(swatch.color.green, 0x7F)
        self.assertEqual(swatch.color.blue, 0xCC)

    def test_offset_calculation(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)

        input = BytesIO(b"STEELExample\x00\x01\x05\x0a\x0b\x0c\x0d\x0e")
        swatch = Swatch(input)

        self.assertEqual(swatch._state.get_offset("version"), 0)
        self.assertEqual(swatch._state.get_offset("color"), 4)

    def test_size_calculation(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)

    def test_attribute_access(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)

    def test_lazy_reading(self):
        class Swatch(Structure):
            version = Integer(size=4)
            color = Object(Color)


class TestNestedVariableObject(unittest.TestCase):
    def test_field_assignment(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=10)

    def test_offset_chain(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=10)

        self.assertEqual(Example._config.offsets["data"], [5, Example.metadata.size])

    def test_greedy_loading(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=5)

        input = BytesIO(b"STEELExample\x00\x01\x05\x0a\x0b\x0c\x0d\x0e")
        example = Example.load(input)

        self.assertEqual(example.tag, b"STEEL")
        self.assertEqual(example.metadata.major_version, 1)
        self.assertEqual(example.metadata.minor_version, 5)
        self.assertEqual(example.data, b"\x0a\x0b\x0c\x0d\x0e")

    def test_offset_calculation(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=5)

        input = BytesIO(b"STEELExample\x00\x01\x05\x0a\x0b\x0c\x0d\x0e")
        example = Example(input)

        self.assertEqual(example._state.get_offset("tag"), 0)
        self.assertEqual(example._state.get_offset("metadata"), 5)
        self.assertEqual(example._state.get_offset("data"), 15)

    def test_size_calculation(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=10)

    def test_attribute_access(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=10)

    def test_lazy_reading(self):
        class Example(Structure):
            tag = FixedBytes(b"STEEL")
            metadata = Object(Metadata)
            data = Bytes(size=10)
