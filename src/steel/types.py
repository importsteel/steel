from io import BufferedIOBase
from typing import Any, Callable, ClassVar

type SizeLookup = Callable[[BufferedIOBase], tuple[int, Any]]


class FieldType[T, D]:
    name: str
    all_options: ClassVar[dict[str, Any]]
    specified_options: dict[str, Any]
    size: int | SizeLookup

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, Any]:
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
