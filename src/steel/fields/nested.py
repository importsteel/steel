from io import SEEK_SET, BufferedIOBase
from typing import TypeVar

from typing_extensions import Buffer

from ..base import Structure
from ..types import SizeLookup
from .base import Field

T = TypeVar("T", bound=Structure)


class OffsetBuffer(BufferedIOBase):
    def __init__(self, buffer: BufferedIOBase, offset: int | None = None):
        self.buffer = buffer
        if offset is None:
            self.offset = buffer.tell()
        else:
            self.offset = offset
            buffer.seek(offset)

    def seekable(self) -> bool:
        return self.buffer.seekable()

    def seek(self, position: int, whence: int = SEEK_SET) -> int:
        return self.buffer.seek(self.offset + position, SEEK_SET)

    def tell(self) -> int:
        return self.buffer.tell() - self.offset

    def readable(self) -> bool:
        return self.buffer.readable()

    def read(self, size: int | None = None) -> bytes:
        return self.buffer.read(size)

    def writable(self) -> bool:
        return self.buffer.writable()

    def write(self, data: Buffer) -> int:
        return self.buffer.write(data)


class Object(Field[T]):
    structure_class: type[T]

    def __init__(self, structure_class: type[T]) -> None:
        self.structure_class = structure_class
        self.size = SizeLookup(self, self.get_size)

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, T]:
        buffer = OffsetBuffer(buffer)
        object = self.structure_class(buffer)
        size = object.get_size(buffer)
        return size, object

    def get_value(self, buffer: BufferedIOBase, cache: T | None = None) -> T:
        buffer = OffsetBuffer(buffer)
        return self.structure_class.load(buffer)
