from ..types import ValidationError
from .base import ExplicitlySizedField


class Bytes(ExplicitlySizedField[bytes]):
    def validate(self, value: bytes) -> None:
        size = len(value)
        if size != self.size:
            raise ValidationError(f"Except {self.size} bytes; got {size}")

    def unpack(self, value: bytes) -> bytes:
        return value

    def pack(self, value: bytes) -> bytes:
        return value


class FixedBytes(Bytes):
    value: bytes

    def __init__(self, value: bytes):
        self.value = value
        super().__init__(size=len(value))

    def validate(self, value: bytes) -> None:
        if value != self.value:
            raise ValidationError(f"Expected {self.value!r}; got {value!r}")

    def get_default(self) -> bytes:
        return self.value
