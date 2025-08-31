from enum import Enum, Flag, IntEnum, StrEnum

from .base import ConversionField, Field, ValidationError
from .numbers import Integer


class EnumField[T: Enum, D](ConversionField[T, D]):
    inner_field: Field[D]
    enum_class: type[T]

    def __init__(self, enum_class: type[T]):
        self.enum_class = enum_class

    def validate(self, value: T) -> None:
        if value not in self.enum_class:
            raise ValidationError(f"{value} is not a valid value for {self.enum_class.__name__}")

    def to_python(self, value: D) -> T:
        return self.enum_class(value)

    def to_data(self, value: T) -> D:
        # `Enum.value` returns `Any`, so we hint it explicitly here.
        data_value: D = value.value
        return data_value


class IntegerEnum(EnumField[IntEnum, int]):
    inner_field: Field[int] = Integer(size=1)


class StringEnum(EnumField[StrEnum, str]):
    inner_field: Field[str]


class Flags(EnumField[Flag, int]):
    inner_field: Field[int] = Integer(size=1)
