from io import BufferedIOBase
from typing import Any, Callable, ClassVar


class FieldType[T, D]:
    name: str
    all_options: ClassVar[dict[str, Any]]
    specified_options: dict[str, Any]
    size: "int | SizeLookup | FieldType[Any, Any]"

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, Any]:
        raise NotImplementedError()

    def get_value(self, buffer: BufferedIOBase, cache: Any) -> T:
        raise NotImplementedError()

    def validate(self, value: Any) -> None:
        pass

    def read(self, buffer: BufferedIOBase) -> tuple[T, int]:
        raise NotImplementedError()

    def write(self, value: T, buffer: BufferedIOBase) -> int:
        raise NotImplementedError()


type AnyField = FieldType[Any, Any]


class ConfigurationType: ...


class StructureType:
    _config: ClassVar[ConfigurationType]


class ConfigurationError(RuntimeError):
    pass


class ValidationError(RuntimeError):
    pass


class SentinelValue:
    pass


class SizeLookup:
    __slots__ = ["field", "func"]

    field: AnyField
    func: Callable[[BufferedIOBase], tuple[int, Any]]

    def __init__(self, field: AnyField, func: Callable[[BufferedIOBase], tuple[int, Any]]) -> None:
        self.field = field
        self.func = func

    def __call__(self, buffer: BufferedIOBase) -> tuple[int, Any]:
        return self.func(buffer)

    @property
    def name(self) -> str:
        return self.field.name
