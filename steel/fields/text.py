from abc import ABC

from .base import Field


class String(ABC, Field[str]):
    encoding: str

    def __init__(self, /, encoding: str):
        self.encoding = encoding

    def decode(self, value: bytes) -> str:
        return value.decode(self.encoding)

    def encode(self, value: str) -> bytes:
        return value.encode(self.encoding)


class FixedLengthString(String):
    size: int

    def __init__(self, /, size: int, encoding: str):
        super().__init__(encoding=encoding)
        self.size = size
