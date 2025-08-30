import unittest
from io import BytesIO
from steel.fields.bytes import Bytes, FixedBytes
from steel.fields.base import ValidationError


class TestBytes(unittest.TestCase):
    def test_validate_correct_size(self):
        field = Bytes(size=4)
        # Should not raise any exception
        field.validate(b"\x00\x01\x02\x03")

    def test_validate_wrong_size(self):
        field = Bytes(size=4)
        with self.assertRaises(ValidationError) as cm:
            field.validate(b"\x00\x01\x02")
        self.assertEqual(str(cm.exception), "Except 4 bytes; got 3")

        with self.assertRaises(ValidationError) as cm:
            field.validate(b"\x00\x01\x02\x03\x04")
        self.assertEqual(str(cm.exception), "Except 4 bytes; got 5")

    def test_encode(self):
        field = Bytes(size=4)
        data = b"\x00\x01\x02\x03"
        encoded = field.encode(data)
        self.assertEqual(encoded, data)

    def test_decode(self):
        field = Bytes(size=4)
        data = b"\x00\x01\x02\x03"
        decoded = field.decode(data)
        self.assertEqual(decoded, data)

    def test_read(self):
        field = Bytes(size=4)
        buffer = BytesIO(b"\x00\x01\x02\x03\x04\x05")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, b"\x00\x01\x02\x03")
        self.assertEqual(bytes_read, 4)

    def test_read_partial(self):
        field = Bytes(size=4)
        buffer = BytesIO(b"\x00\x01")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, b"\x00\x01")
        self.assertEqual(bytes_read, 2)

    def test_write(self):
        field = Bytes(size=4)
        buffer = BytesIO()
        data = b"\x00\x01\x02\x03"
        bytes_written = field.write(data, buffer)
        self.assertEqual(bytes_written, 4)
        buffer.seek(0)
        self.assertEqual(buffer.read(), data)

    def test_different_sizes(self):
        # Test 1-byte field
        field1 = Bytes(size=1)
        self.assertEqual(field1.size, 1)
        field1.validate(b"\xff")

        # Test 8-byte field
        field8 = Bytes(size=8)
        self.assertEqual(field8.size, 8)
        field8.validate(b"\x00\x01\x02\x03\x04\x05\x06\x07")

        # Test 16-byte field
        field16 = Bytes(size=16)
        self.assertEqual(field16.size, 16)
        field16.validate(b"\x00" * 16)

    def test_empty_bytes(self):
        field = Bytes(size=0)
        field.validate(b"")
        self.assertEqual(field.encode(b""), b"")
        self.assertEqual(field.decode(b""), b"")


class TestFixedBytes(unittest.TestCase):
    def test_automatic_size(self):
        data = b"\x00\x01\x02\x03"
        field = FixedBytes(data)
        self.assertEqual(field.value, data)
        self.assertEqual(field.size, 4)

        field = FixedBytes(b"")
        self.assertEqual(field.value, b"")
        self.assertEqual(field.size, 0)

    def test_validate_correct_value(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        # Should not raise any exception
        field.validate(b"\x00\x01\x02\x03")

    def test_validate_wrong_value(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        with self.assertRaises(ValidationError) as cm:
            field.validate(b"\x00\x01\x02\x04")
        self.assertEqual(
            str(cm.exception),
            "Expected b'\\x00\\x01\\x02\\x03'; got b'\\x00\\x01\\x02\\x04'",
        )

    def test_validate_wrong_length(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        with self.assertRaises(ValidationError) as cm:
            field.validate(b"\x00\x01\x02")
        self.assertEqual(
            str(cm.exception),
            "Expected b'\\x00\\x01\\x02\\x03'; got b'\\x00\\x01\\x02'",
        )

    def test_encode(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        # FixedBytes encode should return the input (but validation ensures it's correct)
        encoded = field.encode(b"\x00\x01\x02\x03")
        self.assertEqual(encoded, b"\x00\x01\x02\x03")

    def test_decode(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        decoded = field.decode(b"\x00\x01\x02\x03")
        self.assertEqual(decoded, b"\x00\x01\x02\x03")

    def test_read(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        buffer = BytesIO(b"\x00\x01\x02\x03\x04\x05")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, b"\x00\x01\x02\x03")
        self.assertEqual(bytes_read, 4)

    def test_read_partial(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        buffer = BytesIO(b"\x00\x01")
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, b"\x00\x01")
        self.assertEqual(bytes_read, 2)

    def test_write(self):
        field = FixedBytes(b"\x00\x01\x02\x03")
        buffer = BytesIO()
        # FixedBytes write should use the field's value, not the provided value
        bytes_written = field.write(b"\xff\xff\xff\xff", buffer)
        self.assertEqual(bytes_written, 4)
        buffer.seek(0)
        self.assertEqual(buffer.read(), b"\x00\x01\x02\x03")

    def test_write_ignores_input(self):
        field = FixedBytes(b"MAGIC")
        buffer = BytesIO()
        # Even if we pass different bytes, it should write the fixed value
        bytes_written = field.write(b"OTHER", buffer)
        self.assertEqual(bytes_written, 5)
        buffer.seek(0)
        self.assertEqual(buffer.read(), b"MAGIC")

    def test_common_patterns(self):
        # Test magic numbers
        magic_field = FixedBytes(b"RIFF")
        magic_field.validate(b"RIFF")

        # Test null terminators
        null_field = FixedBytes(b"\x00")
        null_field.validate(b"\x00")

        # Test specific byte patterns
        pattern_field = FixedBytes(b"\xde\xad\xbe\xef")
        pattern_field.validate(b"\xde\xad\xbe\xef")

    def test_single_byte_fixed(self):
        field = FixedBytes(b"\xff")
        self.assertEqual(field.size, 1)
        field.validate(b"\xff")

        with self.assertRaises(ValidationError):
            field.validate(b"\xfe")

    def test_long_fixed_bytes(self):
        long_data = b"\x00" * 100
        field = FixedBytes(long_data)
        self.assertEqual(field.size, 100)
        field.validate(long_data)

        with self.assertRaises(ValidationError):
            field.validate(b"\x00" * 99)
