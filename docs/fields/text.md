# Text Fields

Encode and decode Unicode text with configurable character encodings and other considerations. Strings can come in varying lengths, which can be stored in a few different ways, so there are multiple text fields to handle different behaviors.

## Shared API

All text fields share a common API that's independent of how the bytes are arranged.

### Parameters

- **encoding**: Character encoding to use (e.g., 'utf-8', 'ascii', 'latin-1'). These match Python's native encodings, and there is no default.

### Character vs Byte Length

Most of the following fields also have a `size` parameter, which, like all other fields, refers to the number of bytes that are used to encode the value in a data stream. For many text encodings and termination styles, this can be very different from the number of characters in the decoded string.

```python
field = FixedLengthString(size=5, encoding='utf-8')

# ASCII: 1 byte per character
field.encode('hello')  # b'hello' (5 bytes, which can be stored successfully)

# UTF-8: Variable bytes per character
field.encode('héllo')  # b'h\xc3\xa9llo' (6 bytes, which would exceed the size limit)
```

### Error Handling

String encoding/decoding may raise exceptions for invalid data:

- `UnicodeEncodeError`: When a character cannot be encoded in the target encoding
- `UnicodeDecodeError`: When bytes cannot be decoded using the specified encoding

Consider handling these exceptions or using error handling strategies like `'ignore'` or `'replace'` if needed.

## FixedLengthString

Strings that are always stored in a pre-defined amount of bytes, regardless of the length of the string. The returned value can never be longer than the size of the field, but it can be smaller. 

```python
FixedLengthString(size=20, encoding='ascii')
```

### Additional Parameters

- **size**: Maximum size in bytes for the string data.
- **padding**: Byte to use to pad shorter strings to fit the full length of the field. When reading from a data stream, this padding will automatically be stripped out, and when writing to a stream, it will be added as necessary. (default: b'\x00')
