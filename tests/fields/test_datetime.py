import unittest
from datetime import datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

from steel.fields.datetime import Duration, Timestamp


class TestTimestamp(unittest.TestCase):
    def test_to_data_conversion(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        timestamp = field.to_data(dt)
        self.assertEqual(timestamp, int(dt.timestamp()))

    def test_to_python_conversion(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        timestamp = 1672574400  # 2023-01-01 12:00:00 UTC
        dt = field.to_python(timestamp)
        expected = datetime.fromtimestamp(timestamp, tz=ZoneInfo("UTC"))
        self.assertEqual(dt, expected)

    def test_roundtrip_conversion(self):
        field = Timestamp(timezone=ZoneInfo("UTC"))
        original_dt = datetime(2023, 6, 15, 9, 30, 45, tzinfo=ZoneInfo("UTC"))

        # Convert to data and back
        timestamp = field.to_data(original_dt)
        converted_dt = field.to_python(timestamp)

        # Should be equal (within precision limits)
        self.assertEqual(int(original_dt.timestamp()), int(converted_dt.timestamp()))

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

    def test_timezone_handling(self):
        utc_field = Timestamp(timezone=ZoneInfo("UTC"))
        det_field = Timestamp(timezone=ZoneInfo("America/Detroit"))
        dt_utc = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("UTC"))

        timestamp = utc_field.to_data(dt_utc)
        converted = det_field.to_python(timestamp)
        self.assertEqual(dt_utc, converted)

    def test_different_timestamps(self):
        field = Timestamp()

        # Test epoch
        epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(field.to_data(epoch), 0)
        self.assertEqual(
            field.to_python(0), datetime.fromtimestamp(0, tz=ZoneInfo("UTC"))
        )

        # Test future date
        future = datetime(2050, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("UTC"))
        timestamp = field.to_data(future)
        converted = field.to_python(timestamp)
        self.assertEqual(int(future.timestamp()), int(converted.timestamp()))


class TestDuration(unittest.TestCase):
    def test_to_data_conversion(self):
        field = Duration()
        duration = timedelta(hours=2, minutes=30, seconds=45)
        seconds = field.to_data(duration)
        self.assertEqual(seconds, duration.total_seconds())

    def test_to_python_conversion(self):
        field = Duration()
        seconds = 9045.0  # 2 hours, 30 minutes, 45 seconds
        duration = field.to_python(seconds)
        expected = timedelta(seconds=seconds)
        self.assertEqual(duration, expected)

    def test_roundtrip_conversion(self):
        field = Duration()
        original_duration = timedelta(
            days=1, hours=2, minutes=30, seconds=45, microseconds=123456
        )

        # Convert to data and back
        seconds = field.to_data(original_duration)
        converted_duration = field.to_python(seconds)

        # Should be equal (within precision limits of float)
        self.assertAlmostEqual(
            original_duration.total_seconds(),
            converted_duration.total_seconds(),
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
        self.assertAlmostEqual(
            duration.total_seconds(), read_duration.total_seconds(), places=5
        )

    def test_zero_duration(self):
        field = Duration()
        zero_duration = timedelta()

        self.assertEqual(field.to_data(zero_duration), 0.0)
        self.assertEqual(field.to_python(0.0), timedelta())

    def test_negative_duration(self):
        field = Duration()
        negative_duration = timedelta(seconds=-3600)  # -1 hour

        seconds = field.to_data(negative_duration)
        self.assertEqual(seconds, -3600.0)

        converted = field.to_python(-3600.0)
        self.assertEqual(converted, negative_duration)

    def test_fractional_seconds(self):
        field = Duration()
        duration = timedelta(seconds=1.5)

        seconds = field.to_data(duration)
        self.assertEqual(seconds, 1.5)

        converted = field.to_python(1.5)
        self.assertEqual(converted, duration)

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
                seconds = field.to_data(duration)
                converted = field.to_python(seconds)
                self.assertAlmostEqual(
                    duration.total_seconds(), converted.total_seconds(), places=5
                )
