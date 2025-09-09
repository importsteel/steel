from io import BufferedIOBase
from typing import Any, ClassVar


class FieldType[T, D]:
    name: str
    all_options: ClassVar[dict[str, Any]]
    specified_options: dict[str, Any]

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
