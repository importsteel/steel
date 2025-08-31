import math
import unittest

from steel.fields.base import ValidationError
from steel.fields.numbers import Float, Integer


class TestInteger(unittest.TestCase):
    def test_validate_number_too_big(self):
        field = Integer(size=1, signed=False, endianness=">")

        field.validate(255)
        with self.assertRaises(ValidationError):
            field.validate(256)

        field = Integer(size=1, signed=True, endianness=">")

        field.validate(127)
        with self.assertRaises(ValidationError):
            field.validate(128)

    def test_validate_number_too_small(self):
        field = Integer(size=1, signed=False, endianness=">")

        field.validate(0)
        with self.assertRaises(ValidationError):
            field.validate(-1)

        field = Integer(size=1, signed=True, endianness=">")

        field.validate(-128)
        with self.assertRaises(ValidationError):
            field.validate(-129)

    def test_big_endian_encoding(self):
        field = Integer(size=4, endianness=">")
        packed = field.pack(0x12345678)
        # Most-significant byte first
        self.assertEqual(packed, b"\x12\x34\x56\x78")

    def test_little_endian_encoding(self):
        field = Integer(size=4, endianness="<")
        packed = field.pack(0x12345678)
        # Least-significant byte first
        self.assertEqual(packed, b"\x78\x56\x34\x12")

    def test_big_endian_decoding(self):
        field = Integer(size=4, endianness=">")
        unpacked = field.unpack(b"\x12\x34\x56\x78")
        self.assertEqual(unpacked, 0x12345678)

    def test_little_endian_decoding(self):
        field = Integer(size=4, endianness="<")
        unpacked = field.unpack(b"\x78\x56\x34\x12")
        self.assertEqual(unpacked, 0x12345678)

    def test_signed_encoding(self):
        field = Integer(size=4, signed=True, endianness="<")

        # Positive values
        packed = field.pack(1)
        self.assertEqual(packed, b"\x01\x00\x00\x00")

        # Negative values
        packed = field.pack(-1)
        self.assertEqual(packed, b"\xff\xff\xff\xff")

    def test_signed_decoding(self):
        field = Integer(size=4, signed=True, endianness="<")

        # Positive values
        unpacked = field.unpack(b"\x01\x00\x00\x00")
        self.assertEqual(unpacked, 1)

        # Negative values
        unpacked = field.unpack(b"\xff\xff\xff\xff")
        self.assertEqual(unpacked, -1)

    def test_encoding_sizes(self):
        field = Integer(size=1, endianness="<")
        self.assertEqual(field.pack(255), b"\xff")

        field = Integer(size=2, endianness="<")
        self.assertEqual(field.pack(0x1234), b"\x34\x12")

        field = Integer(size=4, endianness="<")
        self.assertEqual(field.pack(0x12345678), b"\x78\x56\x34\x12")

        field = Integer(size=8, endianness="<")
        self.assertEqual(
            field.pack(0x123456789ABCDEF0), b"\xf0\xde\xbc\x9a\x78\x56\x34\x12"
        )

    def test_decoding_sizes(self):
        field = Integer(size=1, endianness="<")
        self.assertEqual(field.unpack(b"\xff"), 255)

        field = Integer(size=2, endianness="<")
        self.assertEqual(field.unpack(b"\x34\x12"), 0x1234)

        field = Integer(size=4, endianness="<")
        self.assertEqual(field.unpack(b"\x78\x56\x34\x12"), 0x12345678)

        field = Integer(size=8, endianness="<")
        self.assertEqual(
            field.unpack(b"\xf0\xde\xbc\x9a\x78\x56\x34\x12"), 0x123456789ABCDEF0
        )


class TestFloat(unittest.TestCase):
    def test_encoding_sizes(self):
        field = Float(size=2)
        packed = field.pack(0.5)
        self.assertEqual(packed, b"\x008")

        field = Float(size=4)
        packed = field.pack(0.5)
        self.assertEqual(packed, b"\x00\x00\x00?")

        field = Float(size=8)
        packed = field.pack(0.5)
        self.assertEqual(packed, b"\x00\x00\x00\x00\x00\x00\xe0?")

    def test_decoding_sizes(self):
        field = Float(size=2)
        unpacked = field.unpack(b"\x008")
        self.assertEqual(unpacked, 0.5)

        field = Float(size=4)
        unpacked = field.unpack(b"\x00\x00\x00?")
        self.assertEqual(unpacked, 0.5)

        field = Float(size=8)
        unpacked = field.unpack(b"\x00\x00\x00\x00\x00\x00\xe0?")
        self.assertEqual(unpacked, 0.5)

    def test_special_values(self):
        field = Float(size=4)

        # Zero
        packed = field.pack(0.0)
        unpacked = field.unpack(packed)
        self.assertEqual(unpacked, 0.0)

        # Negative zero
        packed = field.pack(-0.0)
        unpacked = field.unpack(packed)
        self.assertEqual(unpacked, -0.0)

        # Infinity
        packed = field.pack(float("inf"))
        unpacked = field.unpack(packed)
        self.assertTrue(math.isinf(unpacked) and unpacked > 0)

        # Negative infinity
        packed = field.pack(float("-inf"))
        unpacked = field.unpack(packed)
        self.assertTrue(math.isinf(unpacked) and unpacked < 0)

        # NaN
        packed = field.pack(float("nan"))
        unpacked = field.unpack(packed)
        self.assertTrue(math.isnan(unpacked))
