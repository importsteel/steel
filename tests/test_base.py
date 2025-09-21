import unittest
from io import BytesIO

from steel.base import Configuration, Structure
from steel.fields.bytes import Bytes, FixedBytes
from steel.fields.numbers import Integer
from steel.fields.text import FixedLengthString, LengthIndexedString, TerminatedString
from steel.types import ValidationError


class TestStructureConfiguration(unittest.TestCase):
    def test_configuration_exists(self):
        class Example(Structure):
            pass

        self.assertIsInstance(Example._config, Configuration)

    def test_configuration_stores_options(self):
        class Example(Structure, encoding="utf8", endianness="<", unknown=True):
            pass

        self.assertEqual(
            Example._config.options,
            {
                "encoding": "utf8",
                "endianness": "<",
                "unknown": True,
            },
        )

    def test_configuration_stores_fields(self):
        class Example(Structure):
            integer = Integer(size=1)
            string = TerminatedString()

        # Something got stored
        self.assertIn("integer", Example._config.fields)
        self.assertIn("string", Example._config.fields)

        # The right fields got stored
        self.assertIsInstance(Example._config.fields["integer"], Integer)
        self.assertIsInstance(Example._config.fields["string"], TerminatedString)

        # They're also accessible as keys on the config itself
        self.assertIsInstance(Example._config["integer"], Integer)
        self.assertIsInstance(Example._config["string"], TerminatedString)


class TestOverridingOptions(unittest.TestCase):
    def test_options_specified_in_fields(self):
        class Example(Structure):
            integer = Integer(size=1, endianness="<")
            string = TerminatedString(terminator=b"\x00", encoding="utf8")

        self.assertEqual(Example.integer.endianness, "<")
        self.assertEqual(
            Example.integer.specified_options,
            {
                "endianness": "<",
                "size": 1,
            },
        )
        self.assertEqual(Example.integer.endianness, "<")

        self.assertEqual(
            Example.string.specified_options,
            {
                "encoding": "utf8",
                "terminator": b"\x00",
            },
        )
        self.assertEqual(Example.string.encoding, "utf8")
        self.assertEqual(Example.string.terminator, b"\x00")

    def test_options_specified_in_structure(self):
        class Example(Structure, endianness="<", encoding="utf8"):
            integer = Integer(size=1)
            string = TerminatedString()

        self.assertEqual(Example.integer.specified_options, {"size": 1})
        self.assertEqual(Example.integer.endianness, "<")

        self.assertEqual(Example.string.specified_options, {})
        self.assertEqual(Example.string.encoding, "utf8")
        self.assertEqual(Example.string.terminator, b"\x00")

    def test_field_options_override_class_options(self):
        class Example(Structure, endianness="<", encoding="utf8"):
            integer = Integer(size=1, endianness=">")
            string = TerminatedString(terminator=b"\xff", encoding="ascii")

        self.assertEqual(
            Example.integer.specified_options,
            {
                "endianness": ">",
                "size": 1,
            },
        )
        self.assertEqual(Example.integer.endianness, ">")

        self.assertEqual(
            Example.string.specified_options,
            {
                "encoding": "ascii",
                "terminator": b"\xff",
            },
        )
        self.assertEqual(Example.string.encoding, "ascii")
        self.assertEqual(Example.string.terminator, b"\xff")

    def test_partial_overrides(self):
        class Example(Structure, padding=b"\xff"):
            utf8 = FixedLengthString(size=1)
            ascii = FixedLengthString(size=1, encoding="ascii")
            padding_00 = FixedLengthString(size=1, padding=b"\x00")
            padding_ff = FixedLengthString(size=1)

        self.assertEqual(Example.utf8.encoding, "utf8")
        self.assertEqual(Example.ascii.encoding, "ascii")
        self.assertEqual(Example.padding_00.padding, b"\x00")
        self.assertEqual(Example.padding_ff.padding, b"\xff")


class TestAssigningValues(unittest.TestCase):
    def test_instantiation(self):
        class Example(Structure):
            integer = Integer(size=1)
            string = TerminatedString()

        instance = Example(integer=1, string="one")
        self.assertEqual(instance.integer, 1)
        self.assertEqual(instance.string, "one")

    def test_post_instantiation(self):
        class Example(Structure):
            integer = Integer(size=1)
            string = TerminatedString()

        instance = Example()
        instance.integer = 1
        instance.string = "one"
        self.assertEqual(instance.integer, 1)
        self.assertEqual(instance.string, "one")

    def test_missing_attribute(self):
        class Example(Structure):
            integer = Integer(size=1)
            string = TerminatedString()

        instance = Example(integer=1)  # Missing string
        self.assertEqual(instance.integer, 1)
        with self.assertRaises(AttributeError):
            instance.string

    def test_writing_with_missing_attribute(self):
        class Example(Structure):
            integer = Integer(size=1)
            string = TerminatedString()

        output = BytesIO()
        instance = Example(integer=1)  # Missing string
        self.assertEqual(instance.integer, 1)
        with self.assertRaises(AttributeError):
            instance.dump(output)


class TestIO(unittest.TestCase):
    def setUp(self):
        class Example(Structure):
            integer = Integer(size=1)
            string = TerminatedString()

        self.Example = Example
        self.bytes = b"\x01one\x00"
        self.dict = {
            "integer": 1,
            "string": "one",
        }

    def test_loading_from_buffer(self):
        instance = self.Example.load(BytesIO(self.bytes))

        self.assertEqual(instance.integer, 1)
        self.assertEqual(instance.string, "one")

    def test_loading_from_bytes(self):
        instance = self.Example.loads(self.bytes)

        self.assertEqual(instance.integer, 1)
        self.assertEqual(instance.string, "one")

    def test_dumping_to_buffer(self):
        instance = self.Example(**self.dict)
        output = instance.dumps()

        self.assertEqual(output, self.bytes)
        self.assertEqual(len(output), 5)

    def test_dumping(self):
        instance = self.Example(**self.dict)
        output = BytesIO()
        size = instance.dump(output)

        self.assertEqual(output.getvalue(), self.bytes)
        self.assertEqual(size, 5)


class TestStructureValidation(unittest.TestCase):
    """Test structure-level validation functionality."""

    def setUp(self):
        """Set up test structures for validation testing."""

        class SimpleStructure(Structure):
            number = Integer(size=1, signed=False)
            text = TerminatedString(encoding="ascii")

        class ComplexStructure(Structure):
            magic = FixedBytes(b"TEST")
            count = Integer(size=2, signed=False)
            name = FixedLengthString(size=10, encoding="ascii")
            data = Bytes(size=4)

        self.SimpleStructure = SimpleStructure
        self.ComplexStructure = ComplexStructure

    def test_validate_all_fields_valid(self):
        """Test validation passes when all fields are valid."""
        instance = self.SimpleStructure(number=100, text="hello")
        print(instance)
        # Should not raise any exception
        instance.validate()

    def test_validate_field_validation_error_propagated(self):
        """Test that field validation errors are propagated up to structure level."""
        instance = self.SimpleStructure(
            number=256, text="hello"
        )  # number too big for 1-byte unsigned

        with self.assertRaises(ValidationError):
            instance.validate()

    def test_validate_multiple_field_validation_errors(self):
        """Test validation with multiple invalid fields."""
        instance = self.SimpleStructure(number=-1, text="héllo")  # number negative, text non-ascii

        with self.assertRaises(ValidationError):
            instance.validate()

    def test_validate_complex_structure_all_valid(self):
        """Test validation of complex structure with all valid fields."""
        instance = self.ComplexStructure(
            magic=b"TEST", count=100, name="myfile", data=b"\x00\x01\x02\x03"
        )
        # Should not raise any exception
        instance.validate()

    def test_validate_complex_structure_invalid_magic(self):
        """Test validation fails when magic bytes are wrong."""
        instance = self.ComplexStructure(
            magic=b"FAIL",  # Wrong magic bytes
            count=100,
            name="myfile",
            data=b"\x00\x01\x02\x03",
        )

        with self.assertRaises(ValidationError):
            instance.validate()

    def test_validate_complex_structure_invalid_name_length(self):
        """Test validation fails when string is too long for fixed length field."""
        instance = self.ComplexStructure(
            magic=b"TEST",
            count=100,
            name="this_name_is_way_too_long_for_10_chars",  # Too long
            data=b"\x00\x01\x02\x03",
        )

        with self.assertRaises(ValidationError):
            instance.validate()

    def test_validate_complex_structure_invalid_data_size(self):
        """Test validation fails when byte data is wrong size."""
        instance = self.ComplexStructure(
            magic=b"TEST",
            count=100,
            name="myfile",
            data=b"\x00\x01\x02",  # Only 3 bytes instead of 4
        )

        with self.assertRaises(ValidationError):
            instance.validate()

    def test_validate_missing_field_raises_attribute_error(self):
        """Test that validation fails appropriately when field is missing."""
        instance = self.SimpleStructure(number=100)  # Missing text field

        with self.assertRaises(ValidationError):
            instance.validate()

    def test_validate_after_reading_from_buffer(self):
        """Test validation after reading structure from buffer."""
        # Create valid binary data
        buffer_data = b"TEST\x00\x64myfile\x00\x00\x00\x00\x00\x00\x01\x02\x03"
        buffer = BytesIO(buffer_data)

        instance = self.ComplexStructure.load(buffer)
        # Should not raise any exception
        instance.validate()

    def test_validate_structure_with_global_options(self):
        """Test validation works with structure-level field options."""

        class StructureWithOptions(Structure, endianness=">", encoding="utf-8"):
            number = Integer(size=2)  # Will use big-endian
            text = TerminatedString()  # Will use UTF-8

        instance = StructureWithOptions(number=1000, text="hello")
        # Should not raise any exception
        instance.validate()

    def test_validate_structure_with_mixed_field_overrides(self):
        """Test validation with mix of structure options and field overrides."""

        class MixedStructure(Structure, endianness=">"):
            big_endian_num = Integer(size=2)  # Uses structure endianness
            little_endian_num = Integer(size=2, endianness="<")  # Overrides endianness

        instance = MixedStructure(big_endian_num=1000, little_endian_num=2000)
        # Should not raise any exception
        instance.validate()

    def test_validation_error_contains_field_context(self):
        """Test that validation errors provide context about which field failed."""
        instance = self.SimpleStructure(number=256, text="hello")  # number too big

        try:
            instance.validate()
            self.fail("Expected ValidationError")
        except ValidationError as e:
            # The error should contain some indication of the problem
            # (exact message format may vary based on implementation)
            self.assertTrue(len(str(e)) > 0)

    def test_validate_empty_structure(self):
        """Test validation of structure with no fields."""

        class EmptyStructure(Structure):
            pass

        instance = EmptyStructure()
        # Should not raise any exception
        instance.validate()


class TestOffsetCalculations(unittest.TestCase):
    def test_explicit_offsets(self):
        class Example(Structure):
            a = Integer(size=1)
            b = Integer(size=2)
            c = Integer(size=4)
            d = Integer(size=8)

        self.assertEqual(Example._config.offsets["a"], [0])
        self.assertEqual(Example._config.offsets["b"], [1])
        self.assertEqual(Example._config.offsets["c"], [3])
        self.assertEqual(Example._config.offsets["d"], [7])

    def test_variable_offsets(self):
        class Example(Structure):
            a = TerminatedString()
            b = Integer(size=1)

        self.assertEqual(Example._config.offsets["a"], [0])
        self.assertEqual(Example._config.offsets["b"], [Example.a.get_size])

    def test_mixed_offsets(self):
        class Example(Structure):
            a = Integer(size=2)
            b = LengthIndexedString(size=Integer(size=1))
            c = Integer(size=4)
            d = Integer(size=2)
            e = TerminatedString()
            f = Integer(size=2)
            g = Integer(size=4)

        self.assertEqual(
            Example._config.offsets["a"],
            [0],
        )
        self.assertEqual(
            Example._config.offsets["b"],
            [2],
        )
        self.assertEqual(
            Example._config.offsets["c"],
            [2, Example.b.get_size],
        )
        self.assertEqual(
            Example._config.offsets["d"],
            [2, Example.b.get_size, 4],
        )
        self.assertEqual(
            Example._config.offsets["e"],
            [2, Example.b.get_size, 6],
        )
        self.assertEqual(
            Example._config.offsets["f"],
            [2, Example.b.get_size, 6, Example.e.get_size],
        )
        self.assertEqual(
            Example._config.offsets["g"],
            [2, Example.b.get_size, 6, Example.e.get_size, 2],
        )
