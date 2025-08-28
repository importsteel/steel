# Number Fields

Encode and decode different kinds of numbers, with configurable options to support a wide range of data formats.

# Integer

The `Integer` field handles integer values with configurable size, signedness, and endianness.

```python
age = Integer(size=1)
birth_year = Integer(size=2, endianness='<')
```

## Parameters

- **size**: Number of bytes (1, 2, 4, or 8)
- **signed**: Whether to interpret as signed integer (default: False)  
- **endianness**: Byte order
  - `'<'` for little-endian (least significant byte first)
  - `'>'` for big-endian (most significant byte first)
  - (default: little-endian)

# Float

The `Float` field handles encoding and decoding of floating-point values to/from binary data using IEEE 754 representation.

```python
price = Float()
```

### Parameters

- **size**: Number of bytes
  - 2 (half precision)
  - 4 (single precision)
  - 8 (double precision)
  - (default: single precision)
