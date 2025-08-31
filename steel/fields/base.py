from abc import abstractmethod
from io import BufferedIOBase
from typing import Optional, Self


class ConfigurationError(RuntimeError):
    pass


class ValidationError(RuntimeError):
    pass


class Field[T]:
    # This looks weird, but it's absolutely critical for type-checking.
    # Fields get assigned to the class as instances of this Field class,
    # but when accessed as attributes on a Structure instance, they'd be
    # native Python types, like str, int and float. Ultimately, the type
    # of the class attribute differs from the instance attribute, even
    # though type-checking tools can't recognize that difference.
    #
    # This __get__ method turns the field into a descriptor, so that code
    # runs whenever the attribute gets accessed, both as a class attribute
    # and as an instance attribute. This code can be understood and
    # interpreted by type checkers, providing an opportunity to add extra
    # type hints about how these attributes will behave. Specifically, the
    # return type(s) of this method will drive how type checkers see the
    # attributes in use elsewhere.
    #
    # There are two return types here:
    #  * Self represents the same type as the field itself. It's Field in
    #    this class, but Self will also reflect subclasses defined elsewhere.
    #  * T represents the native Python type that will be used in instances.
    #    Field is a generic, with the Python type supplied as part of each
    #    definition. So for a field that uses int, it'd be a subclass of
    #    Field[int], which is copied here, which affects how type checkers
    #    interpret that field on instances later down the road.
    def __get__(self, obj: object, obj_type: Optional[type] = None) -> Self | T:
        # This method itself also needs to return a value that satisfies its
        # own return types. If it doesn't return anything, it would implicitly
        # return None, which isn't part of the type definition (but can be done
        # later by using typing's Optional[] type). And T isn't known at the
        # time of the method's definition, so that only leaves Self, which is
        # thankfully easy to return directly.
        #
        # But this code has to actually run, and it will *always* return self.
        # It has nothing to do with T or the final attribute value. What makes
        # this work anyway is that Python will only call the __get__ method if
        # there's no accmopanying value in the instance's __dict__. So as soon
        # as a value is assigned to the attribute, Python will ignore this
        # descriptor anyway. And if a value is *not* assigned to the instance
        # attribute, returning the field object itself is also the right thing
        # to do, matching Python's natural behavior without the descriptor.
        return self

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


class WrappedField[T, D]:
    inner_field: Field[D]

    def get_inner_field(self) -> Field[D]:
        field: Field[D] = self.__class__.__dict__["inner_field"]
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

    @abstractmethod
    def unwrap(self, value: T) -> D:
        raise NotImplementedError()

    def write(self, value: T, buffer: BufferedIOBase) -> int:
        field = self.get_inner_field()
        return field.write(self.unwrap(value), buffer)
