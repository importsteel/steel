from .base import ExplicitlySizedField, ValidationError


class Bytes(ExplicitlySizedField[bytes]):
    def validate(self, value: bytes) -> None:
        size = len(value)
        if size != self.size:
            raise ValidationError(f"Except {self.size} bytes; got {size}")

    def decode(self, value: bytes) -> bytes:
        return value

    def encode(self, value: bytes) -> bytes:
        return value


class FixedBytes(Bytes):
    value: bytes

    def __init__(self, value: bytes):
        self.value = value
        super().__init__(size=len(value))

    def validate(self, value: bytes) -> None:
        if value != self.value:
            raise ValidationError(f"Expected {self.value!r}; got {value!r}")

    def encode(self, value: bytes) -> bytes:
        # Ignore the input value and always write the fixed bytes
        return self.value
