from datetime import (
    datetime,
    timedelta,
)
from zoneinfo import ZoneInfo

from .base import WrappedField
from .numbers import Float, Integer


class Timestamp(WrappedField[datetime, int]):
    inner_field = Integer(size=4)
    timezone: ZoneInfo

    def __init__(self, timezone: ZoneInfo = ZoneInfo("UTC")):
        self.timezone = timezone

    def validate(self, value: datetime) -> None:
        pass

    def unwrap(self, value: datetime) -> int:
        return int(value.timestamp())

    def wrap(self, value: int) -> datetime:
        return datetime.fromtimestamp(value, tz=self.timezone)


class Duration(WrappedField[timedelta, float]):
    inner_field = Float(size=4)

    def validate(self, value: timedelta) -> None:
        pass

    def unwrap(self, value: timedelta) -> float:
        return value.total_seconds()

    def wrap(self, value: float) -> timedelta:
        return timedelta(seconds=value)
