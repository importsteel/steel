from enum import Enum, Flag, IntEnum, StrEnum
from typing import Unpack

from ..types import ValidationError
from .base import BaseParams, Field, WrappedField
from .numbers import Integer


class EnumFieldParams[T](BaseParams[T]):
    pass


class EnumField[T: Enum, D](WrappedField[T, D]):
    enum_class: type[T]
    wrapped_field: Field[D]

    def __init__(
        self,
        enum_class: type[T],
        **kwargs: Unpack[BaseParams[T]],
    ):
        super().__init__(**kwargs)
        self.enum_class = enum_class

    def validate(self, value: T) -> None:
        if value not in self.enum_class:
            raise ValidationError(f"{value} is not a valid value for {self.enum_class.__name__}")

    def wrap(self, value: D) -> T:
        return self.enum_class(value)

    def unwrap(self, value: T) -> D:
        # `Enum.value` returns `Any`, so we hint it explicitly here.
        data_value: D = value.value
        return data_value


class IntegerEnumParams(BaseParams[IntEnum]):
    pass


class IntegerEnum(EnumField[IntEnum, int]):
    wrapped_field: Field[int] = Integer(size=1)


class StringEnumParams(BaseParams[StrEnum]):
    pass


class StringEnum(EnumField[StrEnum, str]):
    wrapped_field: Field[str]

    def __init__(
        self,
        **kwargs: Unpack[BaseParams[StrEnum]],
    ) -> None:
        try:
            self.wrapped_field
            self.enum_class
        except AttributeError:
            raise TypeError("StringEnum must be subclassed with wrapped_field and enum_class")
        super().__init__(enum_class=self.enum_class, **kwargs)


class Flags(EnumField[Flag, int]):
    wrapped_field: Field[int] = Integer(size=1)
