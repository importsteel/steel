from io import BufferedIOBase, BytesIO
from typing import Any, ClassVar, TypeVar

from .types import AnyField, FieldType, SizeLookup, ValidationError

T = TypeVar("T", bound="Structure")


class FieldDict(dict[str, AnyField]): ...


class Configuration:
    fields: FieldDict
    options: dict[str, Any]
    offsets: dict[str, list[int | SizeLookup | AnyField]]

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
        structure_chain: list[int | SizeLookup | AnyField] = []

        for name, field in self.fields.items():
            self.offsets[name] = field_offset = structure_chain.copy()

            if not structure_chain or current_offset > 0:
                field_offset.append(current_offset)

            if isinstance(field.size, FieldType):
                # TODO: Handle field references
                pass
            elif isinstance(field.size, SizeLookup):
                if current_offset > 0:
                    structure_chain.append(current_offset)
                structure_chain.append(field.size)
                current_offset = 0
            else:
                current_offset += field.size

    def create_state(self, buffer: BufferedIOBase) -> "State":
        return State(buffer, self)


class State:
    buffer: BufferedIOBase
    config: Configuration
    cache: dict[str, Any]
    offsets: dict[str, int]
    sizes: dict[str, int]

    def __init__(self, buffer: BufferedIOBase, config: Configuration) -> None:
        self.buffer = buffer
        self.config = config
        self.cache = {}
        self.offsets = {}
        self.sizes = {}

    def get_offset(self, field_name: str) -> int:
        if field_name in self.offsets:
            return self.offsets[field_name]

        offset = 0
        for step in self.config.offsets[field_name]:
            self.buffer.seek(offset)
            if isinstance(step, FieldType):
                # TODO: Handle field references
                pass
            elif isinstance(step, SizeLookup):
                # FIXME: This could handle some cleanup and comments
                if step.name in self.sizes:
                    offset += self.sizes[step.name]
                    continue
                size, cache = step(self.buffer)
                self.sizes[step.name] = size
                offset += size
                self.cache[step.name] = cache
            else:
                offset += step

        self.offsets[field_name] = offset
        return offset

    def get_value(self, field_name: str) -> Any:
        # FIXME: This could handle some cleanup and comments
        if field_name in self.offsets:
            offset = self.offsets[field_name]
        else:
            self.offsets[field_name] = offset = self.get_offset(field_name)
        self.buffer.seek(offset)

        cache = self.cache.get(field_name)
        value, size = self.config[field_name].read(self.buffer, cache=cache)
        self.sizes[field_name] = size
        return value


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

    def __init__(self, buffer: BufferedIOBase | None = None, /, **kwargs: Any) -> None:
        if buffer:
            self._state = self._config.create_state(buffer)

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
