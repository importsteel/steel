# Float Field

The `Float` field handles encoding and decoding of floating-point values to/from binary data using IEEE 754 representation.

## Constructor

```python
Float(size: Literal[2, 4, 8])
```

### Parameters

- **size**: Number of bytes - 2 (half), 4 (single), or 8 (double precision)

## Examples

### Basic Usage

```python
from steel.fields.numbers import Float

# 4-byte single precision float
field = Float(size=4)
encoded = field.encode(0.5)
print(encoded)  # b'\x00\x00\x00?'

decoded = field.decode(b'\x00\x00\x00?')
print(decoded)  # 0.5
```

### Different Precisions

```python
# Half precision (16-bit)
half_field = Float(size=2)
encoded = half_field.encode(0.5)
print(encoded)  # b'\x008'

# Single precision (32-bit) 
single_field = Float(size=4)
encoded = single_field.encode(0.5)
print(encoded)  # b'\x00\x00\x00?'

# Double precision (64-bit)
double_field = Float(size=8)  
encoded = double_field.encode(0.5)
print(encoded)  # b'\x00\x00\x00\x00\x00\x00\xe0?'
```

## Special Values

The Float field properly handles IEEE 754 special values:

### Zero Values

```python
field = Float(size=4)

# Positive zero
encoded = field.encode(0.0)
decoded = field.decode(encoded)
print(decoded)  # 0.0

# Negative zero  
encoded = field.encode(-0.0)
decoded = field.decode(encoded)
print(decoded)  # -0.0
```

### Infinity

```python
import math

field = Float(size=4)

# Positive infinity
encoded = field.encode(float('inf'))
decoded = field.decode(encoded)
print(math.isinf(decoded) and decoded > 0)  # True

# Negative infinity
encoded = field.encode(float('-inf'))  
decoded = field.decode(encoded)
print(math.isinf(decoded) and decoded < 0)  # True
```

### NaN (Not a Number)

```python
import math

field = Float(size=4)

# NaN
encoded = field.encode(float('nan'))
decoded = field.decode(encoded)
print(math.isnan(decoded))  # True
```

## Internal Format Strings

The Float field uses Python's `struct` module with IEEE 754 formats:

| Size | Format | Precision | Range (approx) |
|------|--------|-----------|----------------|
| 2    | 'e'    | Half      | ±6.55 × 10⁴    |
| 4    | 'f'    | Single    | ±3.40 × 10³⁸   |
| 8    | 'd'    | Double    | ±1.80 × 10³⁰⁸  |

## Precision Considerations

### Half Precision (16-bit)
- Limited precision - only ~3-4 significant digits
- Suitable for graphics, machine learning where memory is critical
- May have rounding differences compared to native Python floats

### Single Precision (32-bit)  
- Standard float precision - ~7 significant digits
- Common in graphics, scientific computing
- Good balance of precision and size

### Double Precision (64-bit)
- High precision - ~15-17 significant digits  
- Matches Python's native float type
- Used when precision is critical

## Use Cases

- **Graphics**: Half precision for vertex data, colors
- **Scientific computing**: Single/double precision for calculations
- **File formats**: Binary files with floating-point data
- **Network protocols**: Consistent float representation across platforms
- **Embedded systems**: Interface with hardware using specific float formats