from io import BytesIO


class ReadTracker(BytesIO):
    bytes_read: int = 0

    def read(self, size: int | None = None) -> bytes:
        output = super().read(size)
        self.bytes_read += size or len(output)
        # print("output", output)
        return output
