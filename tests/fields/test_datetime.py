import unittest
from datetime import datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

from steel.fields.datetime import Duration, Timestamp


class TestTimestamp(unittest.TestCase):
    def test_wrapping(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        timestamp = 1672574400  # 2023-01-01 12:00:00 UTC
        dt = field.wrap(timestamp)
        expected = datetime.fromtimestamp(timestamp, tz=ZoneInfo("UTC"))
        self.assertEqual(dt, expected)

    def test_unwrapping(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        timestamp = field.unwrap(dt)
        self.assertEqual(timestamp, int(dt.timestamp()))

    def test_roundtrip(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        original_dt = datetime(2023, 6, 15, 9, 30, 45, tzinfo=ZoneInfo("UTC"))
        roundtrip_dt = field.wrap(field.unwrap(original_dt))

        # Should be equal (within precision limits)
        self.assertEqual(int(original_dt.timestamp()), int(roundtrip_dt.timestamp()))

    def test_reading(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

        buffer = BytesIO(b"\xc0u\xb1c")

        read_dt, size = field.read(buffer)
        self.assertEqual(size, 4)
        self.assertEqual(int(dt.timestamp()), int(read_dt.timestamp()))

    def test_writing(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

        buffer = BytesIO()
        size = field.write(dt, buffer)
        self.assertEqual(buffer.getvalue(), b"\xc0u\xb1c")
        self.assertEqual(size, 4)

    def test_timezone_out_of_utc(self):
        utc_field = Timestamp(timezone=ZoneInfo("UTC"))
        det_field = Timestamp(timezone=ZoneInfo("America/Detroit"))

        # First create a datetime in UTC
        dt_utc = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(dt_utc.tzinfo, ZoneInfo("UTC"))

        # Unwrap it to an int, then re-wrap in a Detroit timezone
        dt_det = det_field.wrap(utc_field.unwrap(dt_utc))
        self.assertEqual(dt_det.tzinfo, ZoneInfo("America/Detroit"))

        # Everything should match *except* the hour
        self.assertEqual(dt_det.year, dt_utc.year)
        self.assertEqual(dt_det.month, dt_utc.month)
        self.assertEqual(dt_det.day, dt_utc.day)
        # In January, Detroit is 5 hours behind UTC
        self.assertEqual(dt_det.hour, dt_utc.hour - 5)
        self.assertEqual(dt_det.minute, dt_utc.minute)
        self.assertEqual(dt_det.second, dt_utc.second)

        # Yet the two will compare equal, because timezone information is retained
        self.assertEqual(dt_utc, dt_det)

    def test_timezone_into_utc(self):
        utc_field = Timestamp(timezone=ZoneInfo("UTC"))

        # First create a datetime in Detroit
        dt_det = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("America/Detroit"))
        self.assertEqual(dt_det.tzinfo, ZoneInfo("America/Detroit"))

        # Unwrap it to an int, then re-wrap in UTC
        dt_utc = utc_field.wrap(utc_field.unwrap(dt_det))
        self.assertEqual(dt_utc.tzinfo, ZoneInfo("UTC"))

        # Everything should match *except* the hour
        self.assertEqual(dt_utc.year, dt_det.year)
        self.assertEqual(dt_utc.month, dt_det.month)
        self.assertEqual(dt_utc.day, dt_det.day)
        # In January, UTC is 5 hours ahead of Detroit
        self.assertEqual(dt_utc.hour, dt_det.hour + 5)
        self.assertEqual(dt_utc.minute, dt_det.minute)
        self.assertEqual(dt_utc.second, dt_det.second)

        # Yet the two will compare equal, because timezone information is retained
        self.assertEqual(dt_utc, dt_det)

    def test_different_timestamps(self):
        field = Timestamp()

        # Test epoch
        epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(field.unwrap(epoch), 0)
        self.assertEqual(field.wrap(0), datetime.fromtimestamp(0, tz=ZoneInfo("UTC")))

        # Test future date
        future = datetime(2050, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("UTC"))
        roundtrip = field.wrap(field.unwrap(future))
        self.assertEqual(int(future.timestamp()), int(roundtrip.timestamp()))

    def test_naive_datetime(self):
        # Try this in multiple timezones, to ensure that it doesn't just
        # get lucky by hitting the local machine's default timezone
        timezone_list = [
            "America/Detroit",
            "America/Los_Angeles",
            "UTC",
        ]

        # Test in a matrix, so that the timezone of the field isn't always the same as the datetime.
        for field_timezone in timezone_list:
            for date_timezone in timezone_list:
                with self.subTest(field_timezone=field_timezone, date_timezone=date_timezone):
                    field = Timestamp(timezone=ZoneInfo(field_timezone))
                    # Creat one with a timezone and one without
                    dt_tz = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo(field_timezone))
                    dt_naive = datetime(2023, 1, 1, 12, 0, 0)

                    # See what happens!
                    naive_timestamp = field.unwrap(dt_naive)
                    converted = field.wrap(naive_timestamp)
                    self.assertEqual(converted, dt_tz)

    def test_get_size(self):
        # Test that Timestamp delegates get_size to wrapped Integer field
        field = Timestamp(timezone=ZoneInfo("UTC"))
        size, cache = field.get_size(BytesIO())

        # Timestamp uses Integer(size=4)
        self.assertEqual(size, 4)


class TestDuration(unittest.TestCase):
    def test_wrapping(self):
        field = Duration()
        seconds = 9045.0  # 2 hours, 30 minutes, 45 seconds
        duration = field.wrap(seconds)
        expected = timedelta(seconds=seconds)
        self.assertEqual(duration, expected)

    def test_unwrapping(self):
        field = Duration()
        duration = timedelta(hours=2, minutes=30, seconds=45)
        seconds = field.unwrap(duration)
        self.assertEqual(seconds, duration.total_seconds())

    def test_roundtrip(self):
        field = Duration()
        original_duration = timedelta(days=1, hours=2, minutes=30, seconds=45, microseconds=123456)
        roundtrip_duration = field.wrap(field.unwrap(original_duration))

        # Should be equal (within precision limits of float)
        self.assertAlmostEqual(
            original_duration.total_seconds(),
            roundtrip_duration.total_seconds(),
            places=5,
        )

    def test_read_write(self):
        field = Duration()
        duration = timedelta(hours=1, minutes=30)

        # Write to buffer
        buffer = BytesIO()
        bytes_written = field.write(duration, buffer)
        self.assertEqual(bytes_written, 4)  # Float size=4

        # Read back from buffer
        buffer.seek(0)
        read_duration, bytes_read = field.read(buffer)
        self.assertEqual(bytes_read, 4)
        self.assertAlmostEqual(duration.total_seconds(), read_duration.total_seconds(), places=5)

    def test_zero_duration(self):
        field = Duration()
        seconds = 0

        self.assertEqual(field.wrap(seconds), timedelta(seconds=seconds))
        self.assertEqual(field.unwrap(timedelta(seconds=seconds)), seconds)

    def test_negative_duration(self):
        field = Duration()
        seconds = -3600  # -1 hour

        self.assertEqual(field.wrap(seconds), timedelta(seconds=seconds))
        self.assertEqual(field.unwrap(timedelta(seconds=seconds)), seconds)

    def test_fractional_seconds(self):
        field = Duration()
        seconds = 1.5

        self.assertEqual(field.wrap(seconds), timedelta(seconds=seconds))
        self.assertEqual(field.unwrap(timedelta(seconds=seconds)), seconds)

    def test_various_durations(self):
        field = Duration()

        test_cases = [
            timedelta(microseconds=1),
            timedelta(milliseconds=1),
            timedelta(seconds=1),
            timedelta(minutes=1),
            timedelta(hours=1),
            timedelta(days=1),
            timedelta(weeks=1),
            timedelta(days=365, hours=12, minutes=30, seconds=45, microseconds=123456),
        ]

        for duration in test_cases:
            with self.subTest(duration=duration):
                roundtrip = field.wrap(field.unwrap(duration))
                self.assertAlmostEqual(
                    duration.total_seconds(),
                    roundtrip.total_seconds(),
                    places=5,
                )

    def test_get_size(self):
        # Test that Duration delegates get_size to wrapped Float field
        field = Duration()
        size, cache = field.get_size(BytesIO())

        # Duration uses Float(size=4)
        self.assertEqual(size, 4)
