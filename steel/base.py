from typing import Any, ClassVar

from .types import AnyField, FieldType


class FieldDict(dict[str, AnyField]): ...


class Configuration:
    fields: FieldDict
    options: dict[str, Any]

    def __init__(self, options: dict[str, Any]) -> None:
        self.fields = FieldDict()
        self.options = options

    def add_field(self, field: AnyField) -> None:
        self.fields[field.name] = field

    def __getitem__(self, name: str) -> AnyField:
        return self.fields[name]


class Structure:
    _config: ClassVar[Configuration]

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
