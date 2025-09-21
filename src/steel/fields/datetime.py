from datetime import (
    datetime,
    timedelta,
)
from typing import NotRequired, Unpack
from zoneinfo import ZoneInfo

from .base import BaseParams, Option, WrappedField
from .numbers import Float, Integer


class TimestampParams(BaseParams[datetime]):
    timezone: NotRequired[ZoneInfo]


class Timestamp(WrappedField[datetime, int]):
    wrapped_field = Integer(size=4)
    timezone: Option[ZoneInfo]

    def __init__(
        self,
        timezone: ZoneInfo = ZoneInfo("UTC"),
        **kwargs: Unpack[BaseParams[datetime]],
    ):
        super().__init__(**kwargs)
        self.timezone = timezone

    def validate(self, value: datetime) -> None:
        pass

    def unwrap(self, value: datetime) -> int:
        if value.tzinfo is None:
            value = datetime(
                year=value.year,
                month=value.month,
                day=value.day,
                hour=value.hour,
                minute=value.minute,
                second=value.second,
                microsecond=value.microsecond,
                tzinfo=self.timezone,  # Add the correct timezone
            )

        return int(value.timestamp())

    def wrap(self, value: int) -> datetime:
        return datetime.fromtimestamp(value, tz=self.timezone)


class DurationParams(BaseParams[timedelta]):
    pass


class Duration(WrappedField[timedelta, float]):
    wrapped_field = Float(size=4)

    def validate(self, value: timedelta) -> None:
        pass

    def unwrap(self, value: timedelta) -> float:
        return value.total_seconds()

    def wrap(self, value: float) -> timedelta:
        return timedelta(seconds=value)
