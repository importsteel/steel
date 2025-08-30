from datetime import (
    datetime,
    timedelta,
)
from zoneinfo import ZoneInfo

from .base import ConversionField
from .numbers import Float, Integer


class Timestamp(ConversionField[datetime, int]):
    inner_field = Integer(size=4)
    timezone: ZoneInfo

    def __init__(self, timezone: ZoneInfo = ZoneInfo("UTC")):
        self.timezone = timezone

    def validate(self, value: datetime) -> None:
        pass

    def to_data(self, value: datetime) -> int:
        return int(value.timestamp())

    def to_python(self, value: int) -> datetime:
        return datetime.fromtimestamp(value, tz=self.timezone)


class Duration(ConversionField[timedelta, float]):
    inner_field = Float(size=4)

    def validate(self, value: timedelta) -> None:
        pass

    def to_data(self, value: timedelta) -> float:
        return value.total_seconds()

    def to_python(self, value: float) -> timedelta:
        return timedelta(seconds=value)
