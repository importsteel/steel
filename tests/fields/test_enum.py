import unittest
from enum import Flag, IntEnum, StrEnum, auto
from io import BytesIO

from steel.fields.enum import Flags, IntegerEnum, StringEnum
from steel.fields.text import FixedLengthString
from steel.types import ConfigurationError, ValidationError


class ByteOrder(IntEnum):
    BIG_ENDIAN = 1
    LITTLE_ENDIAN = 2


class ByteOrderField(IntegerEnum):
    enum_class = ByteOrder


class Status(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class StatusField(StringEnum):
    enum_class = Status
    wrapped_field = FixedLengthString(size=3, encoding="ascii")


class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


class PermissionField(Flags):
    enum_class = Permission


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

    def test_wrapping_valid(self):
        result = self.field.wrap(1)
        self.assertEqual(result, ByteOrder.BIG_ENDIAN)
        self.assertIsInstance(result, ByteOrder)

        result = self.field.wrap(2)
        self.assertEqual(result, ByteOrder.LITTLE_ENDIAN)

    def test_wrapping_invalid_value(self):
        with self.assertRaises(ValueError):
            self.field.wrap(99)

    def test_unwrapping(self):
        self.assertEqual(self.field.unwrap(ByteOrder.BIG_ENDIAN), 1)
        self.assertEqual(self.field.unwrap(ByteOrder.LITTLE_ENDIAN), 2)

    def test_get_size(self):
        # Test that Flags delegates get_size to wrapped Integer field
        size, cache = self.field.get_size(BytesIO())

        # IntegerEnum uses Integer(size=1) by default
        self.assertEqual(size, 1)

    def test_default_value_missing(self):
        field = IntegerEnum(ByteOrder)
        with self.assertRaises(ConfigurationError):
            field.get_default()

    def test_default_value_provided(self):
        field = IntegerEnum(ByteOrder, default=ByteOrder.BIG_ENDIAN)
        self.assertEqual(field.get_default(), ByteOrder.BIG_ENDIAN)


class TestStringEnum(unittest.TestCase):
    def setUp(self):
        class StatusField(StringEnum):
            enum_class = Status
            wrapped_field = FixedLengthString(size=3, encoding="ascii")

        self.field = StatusField()

    def test_validating_valid_value(self):
        self.field.validate(Status.ACTIVE)
        self.field.validate(Status.INACTIVE)
        self.field.validate(Status.PENDING)

    def test_validating_invalid_value(self):
        class OtherEnum(StrEnum):
            OTHER = "other"

        with self.assertRaises(ValidationError):
            self.field.validate(OtherEnum.OTHER)

    def test_wrapping_valid_value(self):
        result = self.field.wrap("active")
        self.assertEqual(result, Status.ACTIVE)
        self.assertIsInstance(result, Status)

        result = self.field.wrap("inactive")
        self.assertEqual(result, Status.INACTIVE)

        result = self.field.wrap("pending")
        self.assertEqual(result, Status.PENDING)

    def test_wrapping_invalid_data(self):
        with self.assertRaises(ValueError):
            self.field.wrap("invalid_status")

    def test_unwrapping(self):
        self.assertEqual(self.field.unwrap(Status.ACTIVE), "active")
        self.assertEqual(self.field.unwrap(Status.INACTIVE), "inactive")
        self.assertEqual(self.field.unwrap(Status.PENDING), "pending")

    def test_subclass_required(self):
        with self.assertRaises(TypeError):
            StringEnum()

    def test_subclass_missing_attributes(self):
        class MissingEnum(StringEnum):
            wrapped_field = FixedLengthString(size=3, encoding="ascii")

        with self.assertRaises(TypeError):
            MissingEnum()

        class MissingField(StringEnum):
            enum_class = Status

        with self.assertRaises(TypeError):
            MissingField()

    def test_get_size(self):
        # Test that Flags delegates get_size to wrapped Integer field
        size, cache = self.field.get_size(BytesIO())

        self.assertEqual(size, 3)

    def test_default_value_missing(self):
        class StatusField(StringEnum):
            enum_class = Status
            wrapped_field = FixedLengthString(size=8, encoding="ascii")

        field = StatusField()
        with self.assertRaises(ConfigurationError):
            field.get_default()

    def test_default_value_provided(self):
        class StatusField(StringEnum):
            enum_class = Status
            wrapped_field = FixedLengthString(size=8, encoding="ascii")

        field = StatusField(default=Status.ACTIVE)
        self.assertEqual(field.get_default(), Status.ACTIVE)


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

    def test_wrapping_single_flag(self):
        result = self.field.wrap(1)
        self.assertEqual(result, Permission.READ)
        self.assertIsInstance(result, Permission)

        result = self.field.wrap(2)
        self.assertEqual(result, Permission.WRITE)

        result = self.field.wrap(4)
        self.assertEqual(result, Permission.EXECUTE)

    def test_wrapping_combined_flags(self):
        result = self.field.wrap(3)
        self.assertEqual(result, Permission.READ | Permission.WRITE)

        result = self.field.wrap(7)
        self.assertEqual(result, Permission.READ | Permission.WRITE | Permission.EXECUTE)

    def test_wrapping_invalid_value(self):
        with self.assertRaises(ValueError):
            self.field.wrap(99)

    def test_unwrapping_single_flag(self):
        self.assertEqual(self.field.unwrap(Permission.READ), 1)
        self.assertEqual(self.field.unwrap(Permission.WRITE), 2)
        self.assertEqual(self.field.unwrap(Permission.EXECUTE), 4)

    def test_unwrapping_combined_flags(self):
        combined = Permission.READ | Permission.WRITE
        self.assertEqual(self.field.unwrap(combined), 3)

        combined = Permission.READ | Permission.WRITE | Permission.EXECUTE
        self.assertEqual(self.field.unwrap(combined), 7)

    def test_get_size(self):
        # Test that Flags delegates get_size to wrapped Integer field
        size, cache = self.field.get_size(BytesIO())

        # Flags uses Integer(size=1) by default
        self.assertEqual(size, 1)

    def test_default_value_missing(self):
        field = Flags(Permission)
        with self.assertRaises(ConfigurationError):
            field.get_default()

    def test_default_value_provided(self):
        all_perms = Permission.READ | Permission.WRITE | Permission.EXECUTE
        field = Flags(Permission, default=all_perms)
        self.assertEqual(field.get_default(), all_perms)
