from io import BufferedIOBase

from .base import Field, ValidationError


class Bytes(Field[bytes]):
    size: int

    def __init__(self, /, size: int):
        self.size = size

    def validate(self, value: bytes) -> None:
        size = len(value)
        if size != self.size:
            raise ValidationError(f'Except {self.size} bytes; got {size}')

    def read(self, buffer: BufferedIOBase) -> tuple[bytes, int]:
        value = buffer.read(self.size)
        return (value, len(value))

    def decode(self, value: bytes) -> bytes:
        return value

    def encode(self, value: bytes) -> bytes:
        return value

    def write(self, value: bytes, buffer: BufferedIOBase) -> int:
        size = buffer.write(value)
        return size


class FixedBytes(Bytes):
    value: bytes
    size: int

    def __init__(self, value: bytes):
        self.value = value
        self.size = len(value)

    def validate(self, value: bytes) -> None:
        if value != self.value:
            raise ValidationError(f'Expected {self.value!r}; got {value!r}')

    def read(self, buffer: BufferedIOBase) -> tuple[bytes, int]:
        value = buffer.read(self.size)
        return (value, len(value))

    def decode(self, value: bytes) -> bytes:
        return value

    def encode(self, value: bytes) -> bytes:
        return value

    def write(self, value: bytes, buffer: BufferedIOBase) -> int:
        size = buffer.write(self.value)
        return size
