# Steel

Steel provides an elegant way to define binary data structures using Python type hints and field descriptors. It's designed to make working with binary file formats intuitive and type-safe.

## Features

- **Declarative**: Define binary structures using familiar Python class syntax
- **Fully type-hinted**: Leverages Python's type hinting system for better IDE support
- **Flexible**: Support for different data types, sizes, and endianness
- **Modern**: Built for Python 3.12+ with modern typing features

## Installation

```bash
pip install steel
```

## Quick Start

```python
import steel

class Header(steel.Structure):
    title = steel.String(8)
    size = steel.Integer(2, endianness='>')

    def __init__(self, title: str, size: int):
        self.title = title
        self.size = size

header = Header(title='Title', size=10)
```

## Field Types

### Requirements
- Python 3.12+
- pytest (for testing)

### Development Setup
```bash
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
```

## Links

- **Homepage**: https://importsteel.org/
- **Issues**: https://github.com/gulopine/steel/issues
