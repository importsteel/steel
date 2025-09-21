from abc import abstractmethod
from io import BufferedIOBase
from types import GenericAlias
from typing import (
    Any,
    Generator,
    NotRequired,
    Optional,
    Self,
    TypeAliasType,
    TypedDict,
    Unpack,
    overload,
)

from ..base import Structure
from ..types import ConfigurationError, FieldType, SentinelValue

# This type can be used to identify field options that can be overriden
# at the class level.
type Option[T] = T

NoDefault = SentinelValue()


class BaseParams[T](TypedDict):
    default: NotRequired[T | SentinelValue]


class Field[T, D = None](FieldType[T, D]):
    default: T | SentinelValue = NoDefault

    @classmethod
    def __init_subclass__(cls: type["Field[T, D]"]) -> None:
        super.__init_subclass__()
        cls.all_options = dict(cls.get_options())

    def __new__(cls: type[Self], *args: Any, **kwargs: Any) -> Self:
        obj: Self = super().__new__(cls)
        obj.specified_options = kwargs
        return obj

    def __init__(self, default: T | SentinelValue = NoDefault):
        self.default = default

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    @classmethod
    def get_options(cls) -> Generator[tuple[str, Any]]:
        for indent, name, annotation in Field.get_all_annotations(cls):
            if not isinstance(annotation, GenericAlias):
                continue
            origin: TypeAliasType = annotation.__origin__  # type: ignore[assignment]
            if origin is Option:
                yield name, annotation.__args__[0]

    @staticmethod
    def get_all_annotations(cls: type, indent: int = 0) -> Generator[tuple[int, str, Any]]:
        if not hasattr(cls, "__annotations__"):
            return
        for name, annotation in cls.__annotations__.items():
            yield indent, name, annotation
        for base in cls.__bases__:
            yield from Field.get_all_annotations(base, indent=indent + 1)

    @abstractmethod
    def get_size(self, buffer: BufferedIOBase) -> tuple[int, Any]:
        raise NotImplementedError()

    @overload
    def __get__(self, obj: None, owner: type) -> Self: ...

    @overload
    def __get__(self, obj: Structure, owner: type) -> T: ...

    @overload
    def __get__(self, obj: Any, owner: type) -> Self: ...

    def __get__(self, obj: Optional[Any], owner: Any) -> Self | T:
        if obj is None:
            return self

        if not isinstance(obj, Structure):
            return self

        try:
            value: T = obj.__dict__[self.name]
        except KeyError:
            try:
                return self.get_default()
            except ConfigurationError:
                raise AttributeError(self.name)
        return value

    @overload
    def __set__(self, instance: Structure, value: T) -> None:
        pass

    @overload
    def __set__(self, instance: Any, value: Any) -> None:
        pass

    def __set__(self, instance: Any, value: Any) -> None:
        instance.__dict__[self.name] = value

    def get_default(self) -> T:
        if isinstance(self.default, SentinelValue):
            raise ConfigurationError("No default value available")
        return self.default

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

    def __init__(self, /, size: int, **kwargs: Unpack[BaseParams[T]]):
        super().__init__(**kwargs)
        self.size = size

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, None]:
        return self.size, None

    def read(self, buffer: BufferedIOBase) -> tuple[T, int]:
        packed = buffer.read(self.size)
        return self.unpack(packed), len(packed)


class WrappedField[T, D](Field[T]):
    wrapped_field: Field[D, Any]

    def get_wrapped_field(self) -> Field[D, Any]:
        # Skip the descriptors when access this internally
        field: Field[D, Any] = self.__class__.__dict__["wrapped_field"]
        return field

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, Any]:
        return self.get_wrapped_field().get_size(buffer)

    @abstractmethod
    def validate(self, value: T) -> None:
        raise NotImplementedError()

    def read(self, buffer: BufferedIOBase) -> tuple[T, int]:
        field = self.get_wrapped_field()
        value, size = field.read(buffer)
        return self.wrap(value), size

    @abstractmethod
    def wrap(self, value: D) -> T:
        raise NotImplementedError()

    def pack(self, value: T) -> bytes:
        field = self.get_wrapped_field()
        return field.pack(self.unwrap(value))

    def unpack(self, value: bytes) -> T:
        field = self.get_wrapped_field()
        return self.wrap(field.unpack(value))

    @abstractmethod
    def unwrap(self, value: T) -> D:
        raise NotImplementedError()

    def write(self, value: T, buffer: BufferedIOBase) -> int:
        field = self.get_wrapped_field()
        return field.write(self.unwrap(value), buffer)
