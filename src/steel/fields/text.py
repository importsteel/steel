from io import SEEK_CUR, BufferedIOBase
from typing import NotRequired, Unpack

from ..types import ConfigurationError, SizeLookup, ValidationError
from .base import BaseParams, Field, Option


class EncodedStringParams(BaseParams[str]):
    encoding: NotRequired[str]


class EncodedString(Field[str]):
    encoding: Option[str]

    def __init__(
        self,
        *,
        encoding: str = "utf8",
        **kwargs: Unpack[BaseParams[str]],
    ):
        super().__init__(**kwargs)
        self.encoding = encoding

    def validate(self, value: str) -> None:
        try:
            value.encode(self.encoding)
        except UnicodeEncodeError as e:
            raise ValidationError(f"{value} could be encoded: {e.reason}")

    def unpack(self, value: bytes) -> str:
        return value.decode(self.encoding)

    def pack(self, value: str) -> bytes:
        return value.encode(self.encoding)


class FixedLengthStringParams(EncodedStringParams):
    size: int
    padding: NotRequired[bytes]


class FixedLengthString(EncodedString):
    size: int
    padding: Option[bytes]

    def __init__(
        self,
        *,
        size: int,
        padding: bytes = b"\x00",
        **kwargs: Unpack[EncodedStringParams],
    ):
        super().__init__(**kwargs)
        if len(padding) > 1:
            raise ConfigurationError(
                f"String padding may only contain one byte; got {len(padding)}"
            )
        self.size = size
        self.padding = padding

    def validate(self, value: str) -> None:
        packed_value = super().pack(value)
        if len(packed_value) > self.size:
            raise ValidationError(f"{value} encodes to more than {self.size} characters")

    def get_size(self, buffer: BufferedIOBase, cache: None = None) -> tuple[int, None]:
        return self.size, None

    def get_value(self, buffer: BufferedIOBase, cache: None) -> str:
        encoded = buffer.read(self.size)
        return self.unpack(encoded)


class LengthIndexedStringParams(EncodedStringParams):
    size_field: NotRequired[Field[int]]


class LengthIndexedString(EncodedString):
    # The byte-length of this string is stored in the data buffer itself,
    # so the size attribute defers to another configured Field type that can
    # return an int type.
    size_field: Field[int]

    def __init__(
        self,
        *,
        size: Field[int],
        **kwargs: Unpack[EncodedStringParams],
    ):
        super().__init__(**kwargs)
        self.size_field = size
        self.size = SizeLookup(self, self.get_size)

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, tuple[int, int]]:
        # Packing the text value will automatically account for the
        # addition of the length field.
        # FIXME: Might be worth a different API to make this more efficient
        text_size, size_size = self.size_field.read(buffer)
        return size_size + text_size, (text_size, size_size)

    def get_value(self, buffer: BufferedIOBase, cache: tuple[int, int]) -> str:
        text_size, size_size = cache
        buffer.seek(size_size, SEEK_CUR)
        encoded = buffer.read(text_size)
        return self.unpack(encoded)

    def pack(self, value: str) -> bytes:
        size_field: Field[int] = self.__dict__["size_field"]

        encoded = super().pack(value)
        size = size_field.pack(len(encoded))

        return size + encoded


class TerminatedStringParams(EncodedStringParams):
    terminator: NotRequired[bytes]


class TerminatedString(EncodedString):
    terminator: Option[bytes]

    def __init__(
        self,
        *,
        terminator: bytes = b"\x00",
        **kwargs: Unpack[EncodedStringParams],
    ):
        super().__init__(**kwargs)
        if len(terminator) > 1:
            raise ConfigurationError(
                f"String terminator may only contain one byte; got {len(terminator)}"
            )
        self.terminator = terminator
        self.size = SizeLookup(self, self.get_size)

    def get_size(self, buffer: BufferedIOBase) -> tuple[int, tuple[bytes, int]]:
        char = buffer.read(1)
        if char == b"":
            return 0, (b"", 0)

        encoded = bytearray()
        while char not in (b"", self.terminator):
            encoded.append(char[0])
            char = buffer.read(1)

        # `char` is either the terminator (if one was found)
        # or an empty string (if the end of the stream was reached).
        # So we use its length to determine how much was actually read.
        size = len(encoded) + len(char)

        return size, (bytes(encoded), size)

    def get_value(self, buffer: BufferedIOBase, cache: tuple[bytes, int]) -> str:
        encoded, size = cache
        buffer.seek(size)

        return self.unpack(encoded)

    def pack(self, value: str) -> bytes:
        encoded = super().pack(value)
        return encoded + self.terminator


# Some aliases for convenience
CString = TerminatedString
PascalString = LengthIndexedString
