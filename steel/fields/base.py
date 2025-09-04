from abc import abstractmethod
from io import BufferedIOBase
from typing import Any, Optional, Self, overload

from ..base import Structure
from ..types import FieldType


class ConfigurationError(RuntimeError):
    pass


class ValidationError(RuntimeError):
    pass


class Field[T, D = None](FieldType[T, D]):
    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @overload
    def __get__(self, obj: None, owner: type) -> Self: ...

    @overload
    def __get__(self, obj: Structure, owner: type) -> T: ...

    @overload
    def __get__(self, obj: Any, owner: type) -> Self: ...

    def __get__(self, obj: Optional[Any], owner: Any) -> Self | T:
        if obj is None or self.name not in obj.__dict__:
            return self
        value: T = obj.__dict__.get(self.name)
        return value

    @overload
    def __set__(self, instance: Structure, value: T) -> None:
        pass

    @overload
    def __set__(self, instance: Any, value: Any) -> None:
        pass

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = value

    @abstractmethod
    def validate(self, value: T) -> None:
        raise NotImplementedError()

    @abstractmethod
    def read(self, buffer: BufferedIOBase) -> tuple[T, int]:
        raise NotImplementedError()

    @abstractmethod
    def pack(self, value: T) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def unpack(self, value: bytes) -> T:
        raise NotImplementedError()

    def write(self, value: T, buffer: BufferedIOBase) -> int:
        # read() methods must all be different in order to know when the value
        # in the buffer is complete, but writing can be more consistent
        # because the packed value already defines how much data to write.
        packed = self.pack(value)
        size = buffer.write(packed)
        return size


class ExplicitlySizedField[T](Field[T]):
    size: int

    def __init__(self, /, size: int):
        self.size = size

    def read(self, buffer: BufferedIOBase) -> tuple[T, int]:
        packed = buffer.read(self.size)
        return self.unpack(packed), len(packed)


class WrappedField[T, D](Field[T, None]):
    inner_field: Field[D, Any]

    def get_inner_field(self) -> Field[D, Any]:
        # Skip the descriptors when access this internally
        field: Field[D, Any] = self.__class__.__dict__["inner_field"]
        return field

    @abstractmethod
    def validate(self, value: T) -> None:
        raise NotImplementedError()

    def read(self, buffer: BufferedIOBase) -> tuple[T, int]:
        field = self.get_inner_field()
        value, size = field.read(buffer)
        return self.wrap(value), size

    @abstractmethod
    def wrap(self, value: D) -> T:
        raise NotImplementedError()

    def pack(self, value: T) -> bytes:
        field = self.get_inner_field()
        return field.pack(self.unwrap(value))

    def unpack(self, value: bytes) -> T:
        field = self.get_inner_field()
        return self.wrap(field.unpack(value))

    @abstractmethod
    def unwrap(self, value: T) -> D:
        raise NotImplementedError()

    def write(self, value: T, buffer: BufferedIOBase) -> int:
        field = self.get_inner_field()
        return field.write(self.unwrap(value), buffer)
