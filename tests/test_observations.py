import io
import json
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from urllib.error import HTTPError

from src.observations import (
    OpenAQAuthenticationError,
    OpenAQClient,
    OpenAQResponseError,
    PM25Observation,
    SensorMetadata,
    parse_pm25_observation,
)


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return io.BytesIO(json.dumps(self.payload).encode("utf-8"))

    def __exit__(self, *args) -> None:
        return None


def measurement(value: float = 42.5) -> dict:
    return {
        "value": value,
        "flagInfo": {"hasFlags": False},
        "parameter": {"id": 2, "name": "pm25", "units": "µg/m³"},
        "period": {
            "label": "1 hour",
            "interval": "01:00:00",
            "datetimeFrom": {"utc": "2026-10-19T00:00:00Z", "local": "2026-10-19T05:30:00+05:30"},
            "datetimeTo": {"utc": "2026-10-19T01:00:00Z", "local": "2026-10-19T06:30:00+05:30"},
        },
        "coordinates": {"latitude": 28.63, "longitude": 77.22},
    }


class ObservationSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sensor = SensorMetadata(101, 22, "PM2.5 sensor", "pm25", "µg/m³")

    def test_parses_traceable_pm25_observation(self) -> None:
        observation = parse_pm25_observation(measurement(), self.sensor)
        self.assertEqual(observation.station_id, 22)
        self.assertEqual(observation.sensor_id, 101)
        self.assertEqual(observation.value, 42.5)
        self.assertEqual(observation.timestamp_utc.tzinfo, timezone.utc)
        self.assertEqual(observation.period_label, "1 hour")

    def test_observation_requires_timezone_and_valid_coordinates(self) -> None:
        with self.assertRaises(ValueError):
            PM25Observation(22, 101, datetime(2026, 1, 1), 10, "µg/m³", 28, 77)
        with self.assertRaises(ValueError):
            PM25Observation(
                22,
                101,
                datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=5, minutes=30))),
                10,
                "µg/m³",
                28,
                77,
            )
        with self.assertRaises(ValueError):
            PM25Observation(
                22, 101, datetime.now(timezone.utc), 10, "µg/m³", 100, 77
            )

    def test_parser_rejects_wrong_parameter_or_unit(self) -> None:
        wrong_parameter = measurement()
        wrong_parameter["parameter"]["name"] = "pm10"
        with self.assertRaises(OpenAQResponseError):
            parse_pm25_observation(wrong_parameter, self.sensor)

        wrong_unit = measurement()
        wrong_unit["parameter"]["units"] = "ppm"
        with self.assertRaises(OpenAQResponseError):
            parse_pm25_observation(wrong_unit, self.sensor)


class OpenAQClientTests(unittest.TestCase):
    def test_requires_api_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(OpenAQAuthenticationError):
                OpenAQClient()

    @patch("src.observations.urlopen")
    def test_filters_pm25_sensors_and_sends_key(self, mocked_urlopen) -> None:
        mocked_urlopen.return_value = FakeResponse(
            {
                "meta": {"found": 2},
                "results": [
                    {"id": 101, "name": "PM", "parameter": {"name": "pm25", "units": "µg/m³"}},
                    {"id": 102, "name": "NO2", "parameter": {"name": "no2", "units": "µg/m³"}},
                ],
            }
        )
        client = OpenAQClient(api_key="secret")
        sensors = client.pm25_sensors_for_location(22)

        self.assertEqual([sensor.sensor_id for sensor in sensors], [101])
        request = mocked_urlopen.call_args.args[0]
        self.assertEqual(request.get_header("X-api-key"), "secret")
        self.assertTrue(request.full_url.endswith("/locations/22/sensors"))

    @patch("src.observations.urlopen")
    def test_paginates_measurements_and_passes_time_range(self, mocked_urlopen) -> None:
        mocked_urlopen.side_effect = [
            FakeResponse({"meta": {"found": 2}, "results": [measurement(10)]}),
            FakeResponse({"meta": {"found": 2}, "results": [measurement(20)]}),
        ]
        client = OpenAQClient(api_key="secret")
        sensor = SensorMetadata(101, 22, "PM", "pm25", "µg/m³")
        observations = client.measurements(
            sensor,
            datetime_from=datetime(2026, 10, 19, tzinfo=timezone.utc),
            datetime_to=datetime(2026, 10, 20, tzinfo=timezone.utc),
            limit=1,
        )

        self.assertEqual([item.value for item in observations], [10, 20])
        urls = [call.args[0].full_url for call in mocked_urlopen.call_args_list]
        self.assertIn("page=1", urls[0])
        self.assertIn("page=2", urls[1])
        self.assertIn("datetime_from=2026-10-19T00%3A00%3A00%2B00%3A00", urls[0])

    @patch("src.observations.urlopen")
    def test_translates_authentication_failure(self, mocked_urlopen) -> None:
        mocked_urlopen.side_effect = HTTPError(
            "https://api.openaq.org", 401, "Unauthorized", {}, None
        )
        client = OpenAQClient(api_key="bad")
        with self.assertRaises(OpenAQAuthenticationError):
            client.sensors_for_location(22)

    @patch("src.observations.urlopen")
    def test_rejects_response_without_results(self, mocked_urlopen) -> None:
        mocked_urlopen.return_value = FakeResponse({"meta": {}})
        client = OpenAQClient(api_key="secret")
        with self.assertRaises(OpenAQResponseError):
            client.sensors_for_location(22)


if __name__ == "__main__":
    unittest.main()
