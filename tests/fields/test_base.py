from io import BytesIO
import unittest

from steel.fields.base import ConversionField
from steel.fields.numbers import Integer


class Structure:
    value = Integer(size=1)

    def __init__(self, value: int):
        # Just to give a way to optionally set an instance value
        if value > 0:
            self.value = value


class IntegerString(ConversionField[str, int]):
    inner_field = Integer(size=2)

    def validate(self, value: str) -> None:
        pass

    def to_data(self, value: str) -> int:
        return int(value)

    def to_python(self, value: int) -> str:
        return str(value)


class TestFieldDescriptor(unittest.TestCase):
    def test_class_attribute(self):
        # Test that the descriptor returns itself when accessed on class
        self.assertIsInstance(Structure.value, Integer)

    def test_unassigned_attribute(self):
        # Test that the descriptor returns itself when no instance value is set
        instance = Structure(0)
        self.assertIsInstance(instance.value, Integer)

    def test_assigned_attribute(self):
        # Test that the field does *not* get returned if an instance value is set
        instance = Structure(10)
        self.assertIsInstance(instance.value, int)


class ConversionBehavior(unittest.TestCase):
    def test_data_field_property(self):
        field = IntegerString()

        self.assertIsInstance(field.inner_field, Integer)

    def test_reading(self):
        field = IntegerString()
        buffer = BytesIO(b"\x05\x00")
        result, bytes_read = field.read(buffer)

        self.assertEqual(bytes_read, 2)
        self.assertEqual(result, "5")

    def test_converting_to_data(self):
        field = IntegerString()
        result = field.to_data("5")

        self.assertEqual(result, 5)

    def test_converting_to_python(self):
        field = IntegerString()
        result = field.to_python(3)

        self.assertEqual(result, "3")

    def test_writing(self):
        field = IntegerString()
        buffer = BytesIO()
        bytes_written = field.write("5", buffer)

        self.assertEqual(bytes_written, 2)
        buffer.seek(0)
        data = buffer.read()
        self.assertEqual(data, b"\x05\x00")
