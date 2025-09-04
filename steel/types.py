from typing import Any, ClassVar


class FieldType[T, D]:
    name: str
    all_options: ClassVar[dict[str, Any]]
    specified_arguments: tuple[Any]
    specified_options: dict[str, Any]


type AnyField = FieldType[Any, Any]


class ConfigurationType: ...


class StructureType:
    _config: ClassVar[ConfigurationType]
