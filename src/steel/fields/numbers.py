import struct
from typing import Literal

from .base import ExplicitlySizedField, Option, ValidationError

INTEGER_FORMATS = {1: "B", 2: "H", 4: "I", 8: "Q"}
FLOAT_FORMATS = {2: "e", 4: "f", 8: "d"}


class Integer(ExplicitlySizedField[int]):
    signed: bool
    endianness: Option[str]

    format: str

    def __init__(
        self,
        size: Literal[1, 2, 4, 8],
        *,
        signed: bool = False,
        endianness: Literal["<", ">"] = "<",
    ):
        super().__init__(size=size)
        self.signed = signed
        self.endianness = endianness
        format = INTEGER_FORMATS[self.size]
        if signed:
            format = format.lower()
        self.format = f"{endianness}{format}"

    def validate(self, value: int) -> None:
        max_value: int = 2 ** (self.size * 8) - 1
        min_value = 0
        if self.signed:
            # Signed values can only be half as high
            max_value //= 2
            # And can extend below zero
            min_value = -1 - max_value

        if value > max_value:
            raise ValidationError(f"{value} is too high")

        if value < min_value:
            raise ValidationError(f"{value} is too low")

    def unpack(self, value: bytes) -> int:
        values = struct.unpack(self.format, value)
        return int(values[0])

    def pack(self, value: int) -> bytes:
        return struct.pack(self.format, value)


class Float(ExplicitlySizedField[float]):
    def __init__(self, size: Literal[2, 4, 8] = 4):
        super().__init__(size=size)
        self.format = FLOAT_FORMATS[size]

    def validate(self, value: float) -> None:
        pass

    def unpack(self, value: bytes) -> float:
        values = struct.unpack(self.format, value)
        return float(values[0])

    def pack(self, value: float) -> bytes:
        return struct.pack(self.format, value)
