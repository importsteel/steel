# Writing fields

The `Field` class is the foundation of the steel.typed library, providing the core functionality for all field types.

## Overview

Fields in steel.typed are implemented as descriptors that enable a powerful pattern: they behave differently when accessed as class attributes versus instance attributes.

## Abstract Methods

All field types must implement:

### `decode(value: bytes) -> T`
Converts bytes to the native Python type.

### `encode(value: T) -> bytes` 
Converts the native Python type to bytes.

## Key Features

- **Descriptor Protocol**: Automatic switching between field and value access
- **Generic Typing**: Full type safety with proper generic constraints  
- **Abstract Base**: Enforces implementation of encode/decode methods
- **Instance Dictionary Bypass**: Uses Python's attribute lookup to avoid calling `__get__` when instance values are set

The descriptor behavior is what enables the elegant API where fields can be accessed for their metadata (size, format, etc.) while also storing actual values on instances.