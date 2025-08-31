import unittest
from enum import Flag, IntEnum, StrEnum, auto

from steel.fields.base import ValidationError
from steel.fields.enum import Flags, IntegerEnum, StringEnum


class ByteOrder(IntEnum):
    BIG_ENDIAN = 1
    LITTLE_ENDIAN = 2


class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


class TestIntegerEnum(unittest.TestCase):
    def setUp(self):
        self.field = IntegerEnum(ByteOrder)

    def test_validating_valid_value(self):
        self.field.validate(ByteOrder.BIG_ENDIAN)
        self.field.validate(ByteOrder.LITTLE_ENDIAN)

    def test_validating_invalid_value(self):
        class OtherEnum(IntEnum):
            OTHER = 99

        with self.assertRaises(ValidationError):
            self.field.validate(OtherEnum.OTHER)

    def test_converting_valid_value_to_python(self):
        result = self.field.to_python(1)
        self.assertEqual(result, ByteOrder.BIG_ENDIAN)
        self.assertIsInstance(result, ByteOrder)

        result = self.field.to_python(2)
        self.assertEqual(result, ByteOrder.LITTLE_ENDIAN)

    def test_converting_invalid_value_to_python(self):
        with self.assertRaises(ValueError):
            self.field.to_python(99)

    def test_converting_to_data(self):
        self.assertEqual(self.field.to_data(ByteOrder.BIG_ENDIAN), 1)
        self.assertEqual(self.field.to_data(ByteOrder.LITTLE_ENDIAN), 2)


class TestStringEnum(unittest.TestCase):
    def setUp(self):
        self.field = StringEnum(Status)

    def test_validating_valid_value(self):
        self.field.validate(Status.ACTIVE)
        self.field.validate(Status.INACTIVE)
        self.field.validate(Status.PENDING)

    def test_validating_invalid_value(self):
        class OtherEnum(StrEnum):
            OTHER = "other"

        with self.assertRaises(ValidationError):
            self.field.validate(OtherEnum.OTHER)

    def test_converting_valid_value_to_python(self):
        result = self.field.to_python("active")
        self.assertEqual(result, Status.ACTIVE)
        self.assertIsInstance(result, Status)

        result = self.field.to_python("inactive")
        self.assertEqual(result, Status.INACTIVE)

        result = self.field.to_python("pending")
        self.assertEqual(result, Status.PENDING)

    def test_converting_invalid_data_to_python(self):
        with self.assertRaises(ValueError):
            self.field.to_python("invalid_status")

    def test_converting_to_data(self):
        self.assertEqual(self.field.to_data(Status.ACTIVE), "active")
        self.assertEqual(self.field.to_data(Status.INACTIVE), "inactive")
        self.assertEqual(self.field.to_data(Status.PENDING), "pending")


class TestFlags(unittest.TestCase):
    def setUp(self):
        self.field = Flags(Permission)

    def test_validating_valid_single_flag(self):
        self.field.validate(Permission.READ)
        self.field.validate(Permission.WRITE)
        self.field.validate(Permission.EXECUTE)

    def test_validating_valid_combined_flags(self):
        combined = Permission.READ | Permission.WRITE
        self.field.validate(combined)

        combined = Permission.READ | Permission.WRITE | Permission.EXECUTE
        self.field.validate(combined)

    def test_validating_invalid_value(self):
        class OtherFlag(Flag):
            OTHER = auto()

        with self.assertRaises(ValidationError):
            self.field.validate(OtherFlag.OTHER)

    def test_to_python_single_flag(self):
        result = self.field.to_python(1)
        self.assertEqual(result, Permission.READ)
        self.assertIsInstance(result, Permission)

        result = self.field.to_python(2)
        self.assertEqual(result, Permission.WRITE)

        result = self.field.to_python(4)
        self.assertEqual(result, Permission.EXECUTE)

    def test_to_python_combined_flags(self):
        result = self.field.to_python(3)
        self.assertEqual(result, Permission.READ | Permission.WRITE)

        result = self.field.to_python(7)
        self.assertEqual(result, Permission.READ | Permission.WRITE | Permission.EXECUTE)

    def test_to_python_invalid_value(self):
        with self.assertRaises(ValueError):
            self.field.to_python(99)

    def test_to_data_single_flag(self):
        self.assertEqual(self.field.to_data(Permission.READ), 1)
        self.assertEqual(self.field.to_data(Permission.WRITE), 2)
        self.assertEqual(self.field.to_data(Permission.EXECUTE), 4)

    def test_to_data_combined_flags(self):
        combined = Permission.READ | Permission.WRITE
        self.assertEqual(self.field.to_data(combined), 3)

        combined = Permission.READ | Permission.WRITE | Permission.EXECUTE
        self.assertEqual(self.field.to_data(combined), 7)
