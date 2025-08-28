from steel.fields.text import FixedLengthString


class TestFixedLengthString:
    def test_ascii_encoding(self):
        field = FixedLengthString(size=5, encoding='ascii')
        encoded = field.encode('hello')
        assert encoded == b'hello'

    def test_ascii_decoding(self):
        field = FixedLengthString(size=5, encoding='ascii')
        decoded = field.decode(b'hello')
        assert decoded == 'hello'

    def test_utf8_encoding(self):
        field = FixedLengthString(size=5, encoding='utf8')
        encoded = field.encode('héllo')
        assert encoded == b'h\xc3\xa9llo'

    def test_utc8_decoding(self):
        field = FixedLengthString(size=5, encoding='utf8')
        decoded = field.decode(b'h\xc3\xa9llo')
        assert decoded == 'héllo'

    def test_emoji(self):
        field = FixedLengthString(size=4, encoding='utf8')
        
        decoded = field.decode(b'\xf0\x9f\x9a\x80')
        assert decoded == '🚀'
        
        encoded = field.encode('🚀')
        assert encoded == b'\xf0\x9f\x9a\x80'
