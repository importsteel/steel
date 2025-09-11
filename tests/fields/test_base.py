import unittest
from io import BytesIO

from steel.base import Structure
from steel.fields.base import WrappedField
from steel.fields.numbers import Integer


class Example(Structure):
    value = Integer(size=1)

    def __init__(self, value: int | None):
        # Just to give a way to optionally set an instance value
        if value is not None:
            self.value = value


class IntegerString(WrappedField[str, int]):
    wrapped_field = Integer(size=2)

    def validate(self, value: str) -> None:
        pass

    def wrap(self, value: int) -> str:
        return str(value)

    def unwrap(self, value: str) -> int:
        return int(value)


class TestFieldDescriptor(unittest.TestCase):
    def test_class_attribute(self):
        # Test that the descriptor returns itself when accessed on class
        self.assertIsInstance(Example.value, Integer)

    def test_unassigned_attribute(self):
        # Test that the descriptor returns itself when no instance value is set
        instance = Example(None)
        with self.assertRaises(AttributeError):
            instance.value

    def test_assigned_attribute(self):
        # Test that the field does *not* get returned if an instance value is set
        instance = Example(10)
        instance.value = 30
        self.assertIsInstance(instance.value, int)


class ConversionBehavior(unittest.TestCase):
    def test_data_field_property(self):
        field = IntegerString()

        self.assertIsInstance(field.wrapped_field, Integer)

    def test_reading(self):
        field = IntegerString()
        buffer = BytesIO(b"\x05\x00")
        result, bytes_read = field.read(buffer)

        self.assertEqual(bytes_read, 2)
        self.assertEqual(result, "5")

    def test_wrapping(self):
        field = IntegerString()
        result = field.wrap(3)

        self.assertEqual(result, "3")

    def test_packing(self):
        field = IntegerString()
        result = field.pack("3")

        self.assertEqual(result, b"\x03\x00")

    def test_unpacking(self):
        field = IntegerString()
        result = field.unpack(b"\x03\x00")

        self.assertEqual(result, "3")

    def test_unwrapping(self):
        field = IntegerString()
        result = field.unwrap("5")

        self.assertEqual(result, 5)

    def test_writing(self):
        field = IntegerString()
        buffer = BytesIO()
        bytes_written = field.write("5", buffer)

        self.assertEqual(bytes_written, 2)
        buffer.seek(0)
        data = buffer.read()
        self.assertEqual(data, b"\x05\x00")

    def test_get_size(self):
        # Test that WrappedField delegates get_size to wrapped field
        field = IntegerString()
        structure = Example(None)
        size = field.get_size(structure)

        # Integer field has size=2
        self.assertEqual(size, 2)
