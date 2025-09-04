import unittest

import steel
from steel.base import Configuration


class TestStructureConfiguration(unittest.TestCase):
    def test_configuration_exists(self):
        class Example(steel.Structure):
            pass

        self.assertIsInstance(Example._config, Configuration)

    def test_configuration_stores_options(self):
        class Example(steel.Structure, encoding="utf8", endianness="<", unknown=True):
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
        class Example(steel.Structure):
            integer = steel.Integer(size=1)
            string = steel.TerminatedString()

        # Something got stored
        self.assertIn("integer", Example._config.fields)
        self.assertIn("string", Example._config.fields)

        # The right fields got stored
        self.assertIsInstance(Example._config.fields["integer"], steel.Integer)
        self.assertIsInstance(Example._config.fields["string"], steel.TerminatedString)

        # They're also accessible as keys on the config itself
        self.assertIsInstance(Example._config["integer"], steel.Integer)
        self.assertIsInstance(Example._config["string"], steel.TerminatedString)


class TestOverridingOptions(unittest.TestCase):
    def test_options_specified_in_fields(self):
        class Example(steel.Structure):
            integer = steel.Integer(size=1, endianness="<")
            string = steel.TerminatedString(terminator=b"\x00", encoding="utf8")

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
        class Example(steel.Structure, endianness="<", encoding="utf8"):
            integer: steel.Integer = steel.Integer(size=1)
            string = steel.TerminatedString()

        self.assertEqual(Example.integer.specified_options, {"size": 1})
        self.assertEqual(Example.integer.endianness, "<")

        self.assertEqual(Example.string.specified_options, {})
        self.assertEqual(Example.string.encoding, "utf8")
        self.assertEqual(Example.string.terminator, b"\x00")

    def test_field_options_override_class_options(self):
        class Example(steel.Structure, endianness="<", encoding="utf8"):
            integer: steel.Integer = steel.Integer(size=1, endianness=">")
            string = steel.TerminatedString(terminator=b"\xff", encoding="ascii")

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
        class Example(steel.Structure, padding=b"\xff"):
            utf8 = steel.FixedLengthString(size=1)
            ascii = steel.FixedLengthString(size=1, encoding="ascii")
            padding_00 = steel.FixedLengthString(size=1, padding=b"\x00")
            padding_ff = steel.FixedLengthString(size=1)

        self.assertEqual(Example.utf8.encoding, "utf8")
        self.assertEqual(Example.ascii.encoding, "ascii")
        self.assertEqual(Example.padding_00.padding, b"\x00")
        self.assertEqual(Example.padding_ff.padding, b"\xff")
