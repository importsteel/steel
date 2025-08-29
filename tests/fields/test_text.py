import unittest
from io import BytesIO

from steel.fields.text import EncodedString, FixedLengthString, LenghIndexedString, TerminatedString
from steel.fields.numbers import Integer
from steel.fields.base import ConfigurationError, ValidationError


class TestStringEncoding(unittest.TestCase):
    def test_ascii_encoding(self):
        field = EncodedString(encoding='ascii')
        encoded = field.encode('hello')
        self.assertEqual(encoded, b'hello')

    def test_ascii_decoding(self):
        field = EncodedString(encoding='ascii')
        decoded = field.decode(b'hello')
        self.assertEqual(decoded, 'hello')

    def test_utf8_encoding(self):
        field = EncodedString(encoding='utf8')
        encoded = field.encode('héllo')
        self.assertEqual(encoded, b'h\xc3\xa9llo')

    def test_utf8_decoding(self):
        field = EncodedString(encoding='utf8')
        decoded = field.decode(b'h\xc3\xa9llo')
        self.assertEqual(decoded, 'héllo')

    def test_emoji(self):
        field = EncodedString(encoding='utf8')
        
        decoded = field.decode(b'\xf0\x9f\x9a\x80')
        self.assertEqual(decoded, '🚀')
        
        encoded = field.encode('🚀')
        self.assertEqual(encoded, b'\xf0\x9f\x9a\x80')

    def test_validation(self):
        field = EncodedString(encoding='ascii')
        
        field.validate('hello')
        with self.assertRaises(ValidationError):
            field.validate('héllo')


class TestFixedLengthString(unittest.TestCase):
    def test_invalid_padding(self):
        with self.assertRaises(ConfigurationError):
            FixedLengthString(encoding='utf-8', size=10, padding=b'too_long')

    def test_reading(self):
        field = FixedLengthString(encoding='utf-8', size=10)

        buffer = BytesIO(b'hello\x00\x00\x00\x00\x00')
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, 'hello\x00\x00\x00\x00\x00')
        self.assertEqual(bytes_read, 10)

    def test_writing(self):
        field = FixedLengthString(encoding='utf-8', size=10)

        buffer = BytesIO()
        bytes_written = field.write('hello', buffer)
        self.assertEqual(bytes_written, 5)

        buffer.seek(0)
        data = buffer.read()
        self.assertEqual(data, b'hello')


class TestLenghIndexedString(unittest.TestCase):
    def test_reading(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding='ascii')

        buffer = BytesIO(b'\x05hello')
        value, size = field.read(buffer)
        self.assertEqual(value, 'hello')
        self.assertEqual(size, 6)

    def test_reading_ignores_extra_data(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding='ascii')

        buffer = BytesIO(b'\x05hello:more_data')
        value, size = field.read(buffer)
        self.assertEqual(value, 'hello')
        self.assertEqual(size, 6)

    def test_reading_empty_string(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding='ascii')

        buffer = BytesIO(b'\x00')
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, '')
        self.assertEqual(bytes_read, 1)

    def test_writing(self):
        size_field = Integer(size=1)
        field = LenghIndexedString(size=size_field, encoding='ascii')

        buffer = BytesIO()
        bytes_written = field.write('hello', buffer)
        self.assertEqual(bytes_written, 6)

        buffer.seek(0)
        data = buffer.getvalue()
        self.assertEqual(data, b'\x05hello')


class TestTerminatedString(unittest.TestCase):
    def test_invalid_terminator(self):
        with self.assertRaises(ConfigurationError):
            TerminatedString(encoding='utf-8', terminator=b'toolong')

    def test_reading(self):
        field = TerminatedString(encoding='utf-8', terminator=b'\x00')

        buffer = BytesIO(b'hello\x00')
        value, size = field.read(buffer)
        self.assertEqual(value, 'hello')
        self.assertEqual(size, 6)

    def test_reading_with_custom_terminator(self):
        field = TerminatedString(encoding='utf-8', terminator=b';')

        buffer = BytesIO(b'hello;')
        value, size = field.read(buffer)
        self.assertEqual(value, 'hello')
        self.assertEqual(size, 6)

    def test_reading_ignores_extra_data(self):
        field = TerminatedString(encoding='utf-8', terminator=b'\x00')

        buffer = BytesIO(b'hello\x00more_data')
        value, size = field.read(buffer)
        self.assertEqual(value, 'hello')
        self.assertEqual(size, 6)

    def test_reading_empty_string(self):
        field = TerminatedString(encoding='utf-8', terminator=b'\x00')

        buffer = BytesIO(b'\x00')
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, '')
        self.assertEqual(bytes_read, 1)

    def test_reading_eof(self):
        field = TerminatedString(encoding='utf-8', terminator=b'\x00')

        buffer = BytesIO(b'')
        value, bytes_read = field.read(buffer)
        self.assertEqual(value, '')
        self.assertEqual(bytes_read, 0)

    def test_writing(self):
        field = TerminatedString(encoding='ascii')

        buffer = BytesIO()
        bytes_written = field.write('hello', buffer)
        self.assertEqual(bytes_written, 6)

        buffer.seek(0)
        data = buffer.getvalue()
        self.assertEqual(data, b'hello\x00')
