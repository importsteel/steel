from io import BufferedIOBase, BufferedReader, BytesIO
from typing import Any, ClassVar, TypeVar

from .types import AnyField, FieldType, SizeLookup, ValidationError

T = TypeVar("T", bound="Structure")


class FieldDict(dict[str, AnyField]): ...


class Configuration:
    fields: FieldDict
    options: dict[str, Any]
    offsets: dict[str, list[int | SizeLookup]]

    def __init__(self, options: dict[str, Any]) -> None:
        self.fields = FieldDict()
        self.options = options
        self.offsets = {}

    def add_field(self, field: AnyField) -> None:
        self.fields[field.name] = field

    def __getitem__(self, name: str) -> AnyField:
        return self.fields[name]

    def create_offset_chains(self) -> None:
        current_offset = 0
        structure_chain: list[int | SizeLookup] = []

        for name, field in self.fields.items():
            self.offsets[name] = field_offset = structure_chain.copy()

            if not structure_chain or current_offset > 0:
                field_offset.append(current_offset)

            if callable(field.size):
                if current_offset > 0:
                    structure_chain.append(current_offset)
                structure_chain.append(field.size)
                current_offset = 0
            else:
                current_offset += field.size


class FieldState:
    __slots__ = ["field", "offset_chain", "size", "cache"]

    field: AnyField
    offset: int | None
    size: int | None
    cache: Any

    def __init__(self, field: AnyField, /) -> None:
        self.field = field


class State(dict[str, FieldState]):
    buffer: BufferedReader | None

    def __init__(self, buffer: BufferedReader | None, config: Configuration) -> None:
        self.buffer = buffer
        self.config = config


class Structure:
    _config: ClassVar[Configuration]
    _state: State

    def __init_subclass__(cls, **options: Any) -> None:
        super().__init_subclass__()
        override_keys = set(options.keys())
        cls._config = Configuration(options=options)
        for attr in cls.__dict__.values():
            if not isinstance(attr, FieldType):
                continue
            # Just to make it clear from here on out
            field = attr
            cls._config.add_field(field)

            if not override_keys:
                # No extra options passed in, so there's nothing more to do with this field
                continue

            overrides = override_keys & set(field.all_options) - set(field.specified_options)
            for key in overrides:
                setattr(field, key, options[key])

        cls._config.create_offset_chains()

    def __init__(self, buffer: BufferedReader | None = None, /, **kwargs: Any) -> None:
        self._state = State(buffer, self.__class__._config)

        # FIXME: This needs to be *a lot* smarter, but it proves the basic idea for now
        for key, value in kwargs.items():
            setattr(self, key, value)

    def validate(self) -> None:
        for field in self.__class__._config.fields.values():
            if not hasattr(self, field.name):
                raise ValidationError(f"{field.name} has no value")
            value = getattr(self, field.name)
            field.validate(value)

    @classmethod
    def load(cls: type[T], buffer: BufferedIOBase) -> T:
        data = {}
        for field in cls._config.fields.values():
            data[field.name], size = field.read(buffer)
        return cls(**data)

    @classmethod
    def loads(cls: type[T], value: bytes) -> T:
        return cls.load(BytesIO(value))

    def dump(self, buffer: BufferedIOBase) -> int:
        size = 0
        for field in self.__class__._config.fields.values():
            value = getattr(self, field.name)
            size += field.write(value, buffer)
        return size

    def dumps(self) -> bytes:
        output = BytesIO()
        self.dump(output)
        return output.getvalue()
