from steel.fields.numbers import Integer


class TestInteger:
    def test_big_endian_encoding(self):
        field = Integer(size=4, endianness='>')
        encoded = field.encode(0x12345678)
        # Most-significant byte first
        assert encoded == b'\x12\x34\x56\x78'

    def test_little_endian_encoding(self):
        field = Integer(size=4, endianness='<')
        encoded = field.encode(0x12345678)
        # Least-significant byte first
        assert encoded == b'\x78\x56\x34\x12'

    def test_big_endian_decoding(self):
        field = Integer(size=4, endianness='>')
        decoded = field.decode(b'\x12\x34\x56\x78')
        assert decoded == 0x12345678

    def test_little_endian_decoding(self):
        field = Integer(size=4, endianness='<')
        decoded = field.decode(b'\x78\x56\x34\x12')
        assert decoded == 0x12345678

    def test_signed_encoding(self):
        field = Integer(size=4, signed=True, endianness='<')

        # Positive values
        encoded = field.encode(1)
        assert encoded == b'\x01\x00\x00\x00'

        # Negative values
        encoded = field.encode(-1)
        assert encoded == b'\xff\xff\xff\xff'

    def test_signed_decoding(self):
        field = Integer(size=4, signed=True, endianness='<')

        # Positive values
        decoded = field.decode(b'\x01\x00\x00\x00')
        assert decoded == 1

        # Negative values
        decoded = field.decode(b'\xff\xff\xff\xff')
        assert decoded == -1

    def test_encoding_sizes(self):
        field = Integer(size=1, endianness='<')
        assert field.encode(255) == b'\xff'

        field = Integer(size=2, endianness='<')
        assert field.encode(0x1234) == b'\x34\x12'

        field = Integer(size=4, endianness='<')
        assert field.encode(0x12345678) == b'\x78\x56\x34\x12'

        field = Integer(size=8, endianness='<')
        assert field.encode(0x123456789abcdef0) == b'\xf0\xde\xbc\x9a\x78\x56\x34\x12'

    def test_decoding_sizes(self):
        field = Integer(size=1, endianness='<')
        assert field.decode(b'\xff') == 255

        field = Integer(size=2, endianness='<')
        assert field.decode(b'\x34\x12') == 0x1234

        field = Integer(size=4, endianness='<')
        assert field.decode(b'\x78\x56\x34\x12') == 0x12345678

        field = Integer(size=8, endianness='<')
        assert field.decode(b'\xf0\xde\xbc\x9a\x78\x56\x34\x12') == 0x123456789abcdef0


class TestFloat:
    def test_encoding_sizes(self):
        from steel.fields.numbers import Float

        field = Float(size=2)
        encoded = field.encode(0.5)
        assert encoded == b'\x008'

        field = Float(size=4)
        encoded = field.encode(0.5)
        assert encoded == b'\x00\x00\x00?'

        field = Float(size=8)
        encoded = field.encode(0.5)
        assert encoded == b'\x00\x00\x00\x00\x00\x00\xe0?'

    def test_decoding_sizes(self):
        from steel.fields.numbers import Float

        field = Float(size=2)
        decoded = field.decode(b'\x008')
        assert decoded == 0.5

        field = Float(size=4)
        decoded = field.decode(b'\x00\x00\x00?')
        assert decoded == 0.5

        field = Float(size=8)
        decoded = field.decode(b'\x00\x00\x00\x00\x00\x00\xe0?')
        assert decoded == 0.5

    def test_special_values(self):
        from steel.fields.numbers import Float
        import math

        field = Float(size=4)

        # Zero
        encoded = field.encode(0.0)
        decoded = field.decode(encoded)
        assert decoded == 0.0

        # Negative zero
        encoded = field.encode(-0.0)
        decoded = field.decode(encoded)
        assert decoded == -0.0

        # Infinity
        encoded = field.encode(float('inf'))
        decoded = field.decode(encoded)
        assert math.isinf(decoded) and decoded > 0

        # Negative infinity
        encoded = field.encode(float('-inf'))
        decoded = field.decode(encoded)
        assert math.isinf(decoded) and decoded < 0

        # NaN
        encoded = field.encode(float('nan'))
        decoded = field.decode(encoded)
        assert math.isnan(decoded)
