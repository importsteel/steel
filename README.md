# Steel

Steel provides an elegant way to define binary data structures using Python type hints and field
descriptors. It's designed to make working with binary file formats intuitive and type-safe.

## Features

- **Declarative**: Define binary structures using familiar Python class syntax
- **Fully type-hinted**: Leverage your IDE to interact with binary data
- **Flexible**: Support for different data types, sizes, and endianness
- **Modern**: Built for Python 3.13+ with modern typing features

## Installation

```bash
pip install steel
```

## Quick Start

```python
import steel

class GIF(steel.Structure):
    magic = steel.FixedBytes(b'GIF')
    version = steel.FixedLengthString(size=3)
    width = steel.Integer(size=2)
    height = steel.Integer(size=2)

with open('logo.gif', 'rb') as f:
    image = GIF.read(f)

print(f"Version: {image.version}")
print(f"Version: {header.version}")
print(f"Size: {header.width}x{header.height}")
```

## Requirements
- Python 3.13+

## Development Setup
```bash
pip install -e ".[dev]"
```

## Links

- **Homepage**: https://importsteel.org/
- **Issues**: https://github.com/gulopine/steel/issues
