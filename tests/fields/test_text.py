import unittest
from io import BytesIO

from steel.fields.numbers import Integer
from steel.fields.text import (
    EncodedString,
    FixedLengthString,
    LenghIndexedString,
    TerminatedString,
)
from steel.types import ConfigurationError, ValidationError


class TestStringEncoding(unittest.TestCase):
    def test_ascii_encoding(self):
        field = EncodedString(encoding="ascii")
        packed = field.pack("hello")
        self.assertEqual(packed, b"hello")

    def test_ascii_decoding(self):
        field = EncodedString(encoding="ascii")
        unpacked = field.unpack(b"hello")
        self.assertEqual(unpacked, "hello")

    def test_utf8_encoding(self):
        field = EncodedString(encoding="utf8")
        packed = field.pack("héllo")
        self.assertEqual(packed, b"h\xc3\xa9llo")

    def test_utf8_decoding(self):
        field = EncodedString(encoding="utf8")
        unpacked = field.unpack(b"h\xc3\xa9llo")
        self.assertEqual(unpacked, "héllo")

    def test_emoji(self):
        field = EncodedString(encoding="utf8")

        unpacked = field.unpack(b"\xf0\x9f\x9a\x80")
        self.assertEqual(unpacked, "🚀")

        packed = field.pack("🚀")
        self.assertEqual(packed, b"\xf0\x9f\x9a\x80")

    def test_validation(self):
        field = EncodedString(encoding="ascii")

        field.validate("hello")
        with self.assertRaises(ValidationError):
            field.validate("héllo")


class TestFixedLengthString(unittest.TestCase):
    def test_invalid_padding(self):
        with self.assertRaises(ConfigurationError):
            FixedLengthString(encoding="utf-8", size=10, padding=b"too_long")

    def test_reading(self):
        field = FixedLengthString(encoding="utf-8", size=10)

        buffer = BytesIO(b"hello\x00\x00\x00\x00\x00")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, "hello\x00\x00\x00\x00\x00")
        self.assertEqual(bytes_read, 10)

    def test_writing(self):
        field = FixedLengthString(encoding="utf-8", size=10)

        buffer = BytesIO()
        bytes_written = field.write("hello", buffer)
        self.assertEqual(bytes_written, 5)

        buffer.seek(0)
        data = buffer.read()
        self.assertEqual(data, b"hello")

    def test_get_size(self):
        field = FixedLengthString(size=20, encoding="ascii")

        size, cache = field.get_size(BytesIO(b"hello"))

        self.assertEqual(size, 20)

    def test_different_size_values(self):
        field = FixedLengthString(size=20, encoding="ascii")

        # Always the specified size, no matter the length of the string
        size, cache = field.get_size(BytesIO(b"hello"))
        self.assertEqual(size, 20)
        self.assertIsNone(cache)

        size, cache = field.get_size(BytesIO(b"hello world"))
        self.assertEqual(size, 20)
        self.assertIsNone(cache)

        size, cache = field.get_size(BytesIO(b"hello to the big blue world"))
        self.assertEqual(size, 20)
        self.assertIsNone(cache)


class TestLenghIndexedString(unittest.TestCase):
    def test_reading(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding="ascii")

        buffer = BytesIO(b"\x05hello")
        value, size = field.read(buffer)
        self.assertEqual(value, "hello")
        self.assertEqual(size, 6)

    def test_reading_ignores_extra_data(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding="ascii")

        buffer = BytesIO(b"\x05hello:more_data")
        value, size = field.read(buffer)
        self.assertEqual(value, "hello")
        self.assertEqual(size, 6)

    def test_reading_empty_string(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding="ascii")

        buffer = BytesIO(b"\x00")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, "")
        self.assertEqual(bytes_read, 1)

    def test_writing(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding="ascii")

        buffer = BytesIO()
        bytes_written = field.write("hello", buffer)
        self.assertEqual(bytes_written, 6)

        buffer.seek(0)
        data = buffer.getvalue()
        self.assertEqual(data, b"\x05hello")

    def test_get_size(self):
        field = LenghIndexedString(size=Integer(size=2), encoding="ascii")

        size, cache = field.get_size(BytesIO(b"\x05\x00hello"))

        # Size includes the 2-byte length at the beginning
        self.assertEqual(size, 7)

    def test_different_size_fields(self):
        field = LenghIndexedString(size=Integer(size=1), encoding="ascii")
        size, cache = field.get_size(BytesIO(b"\x05hello"))
        self.assertEqual(size, 6)

        field = LenghIndexedString(size=Integer(size=4), encoding="ascii")
        size, cache = field.get_size(BytesIO(b"\x05\x00\x00\x00hello"))
        self.assertEqual(size, 9)


class TestTerminatedString(unittest.TestCase):
    def test_invalid_terminator(self):
        with self.assertRaises(ConfigurationError):
            TerminatedString(encoding="utf-8", terminator=b"toolong")

    def test_reading(self):
        field = TerminatedString(encoding="utf-8", terminator=b"\x00")

        buffer = BytesIO(b"hello\x00")
        value, size = field.read(buffer)
        self.assertEqual(value, "hello")
        self.assertEqual(size, 6)

    def test_reading_with_custom_terminator(self):
        field = TerminatedString(encoding="utf-8", terminator=b";")

        buffer = BytesIO(b"hello;")
        value, size = field.read(buffer)
        self.assertEqual(value, "hello")
        self.assertEqual(size, 6)

    def test_reading_ignores_extra_data(self):
        field = TerminatedString(encoding="utf-8", terminator=b"\x00")

        buffer = BytesIO(b"hello\x00more_data")
        value, size = field.read(buffer)
        self.assertEqual(value, "hello")
        self.assertEqual(size, 6)

    def test_reading_empty_string(self):
        field = TerminatedString(encoding="utf-8", terminator=b"\x00")

        buffer = BytesIO(b"\x00")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, "")
        self.assertEqual(bytes_read, 1)

    def test_reading_eof(self):
        field = TerminatedString(encoding="utf-8", terminator=b"\x00")

        buffer = BytesIO(b"")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, "")
        self.assertEqual(bytes_read, 0)

    def test_writing(self):
        field = TerminatedString(encoding="ascii")

        buffer = BytesIO()
        bytes_written = field.write("hello", buffer)
        self.assertEqual(bytes_written, 6)

        buffer.seek(0)
        data = buffer.getvalue()
        self.assertEqual(data, b"hello\x00")

    def test_get_size(self):
        field = TerminatedString(encoding="ascii")

        # Test TerminatedString get_size returns minimum size (terminator)
        size, cache = field.get_size(BytesIO(b"hello"))

        # Size includes the terminator
        self.assertEqual(size, 6)
        self.assertEqual(cache, "hello")
