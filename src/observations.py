"""Typed OpenAQ v3 data access for PM2.5 observations."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OPENAQ_BASE_URL = "https://api.openaq.org/v3"


class OpenAQError(RuntimeError):
    """Base exception for OpenAQ client failures."""


class OpenAQAuthenticationError(OpenAQError):
    """Raised when an API key is missing or rejected."""


class OpenAQResponseError(OpenAQError):
    """Raised when OpenAQ returns an invalid or unexpected response."""


@dataclass(frozen=True, slots=True)
class SensorMetadata:
    """A single sensor and the parameter it measures at an OpenAQ location."""

    sensor_id: int
    station_id: int
    name: str
    parameter: str
    unit: str

    @property
    def is_pm25(self) -> bool:
        return self.parameter.lower() == "pm25"


@dataclass(frozen=True, slots=True)
class PM25Observation:
    """One traceable PM2.5 measurement reported by OpenAQ."""

    station_id: int
    sensor_id: int
    timestamp_utc: datetime
    value: float
    unit: str
    latitude: float
    longitude: float
    source: str = "OpenAQ"
    has_flags: bool = False
    period_label: str | None = None

    def __post_init__(self) -> None:
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("timestamp_utc must include timezone information")
        if self.timestamp_utc.utcoffset() != timedelta(0):
            raise ValueError("timestamp_utc must use UTC")
        if not self.unit.strip():
            raise ValueError("unit cannot be empty")
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")


def _parse_datetime(value: Any, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise OpenAQResponseError(f"{field_name} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise OpenAQResponseError(f"invalid {field_name}: {value}") from error
    if parsed.tzinfo is None:
        raise OpenAQResponseError(f"{field_name} must include a timezone")
    return parsed


def parse_sensor(result: dict[str, Any], station_id: int) -> SensorMetadata:
    """Validate and convert one OpenAQ sensor response object."""
    try:
        parameter = result["parameter"]
        return SensorMetadata(
            sensor_id=int(result["id"]),
            station_id=station_id,
            name=str(result["name"]),
            parameter=str(parameter["name"]),
            unit=str(parameter["units"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise OpenAQResponseError("invalid sensor response object") from error


def parse_pm25_observation(
    result: dict[str, Any], sensor: SensorMetadata
) -> PM25Observation:
    """Validate and convert one measurement from a known PM2.5 sensor."""
    if not sensor.is_pm25:
        raise ValueError(f"sensor {sensor.sensor_id} does not measure PM2.5")

    try:
        parameter = result["parameter"]
        if str(parameter["name"]).lower() != "pm25":
            raise OpenAQResponseError("measurement parameter is not PM2.5")
        unit = str(parameter["units"])
        if unit != sensor.unit:
            raise OpenAQResponseError(
                f"measurement unit {unit!r} does not match sensor unit {sensor.unit!r}"
            )

        period = result["period"]
        timestamp_object = period.get("datetimeTo") or period.get("datetimeFrom")
        coordinates = result["coordinates"]
        value = result["value"]
        if value is None or coordinates is None or timestamp_object is None:
            raise OpenAQResponseError("measurement is missing value, coordinates, or time")

        return PM25Observation(
            station_id=sensor.station_id,
            sensor_id=sensor.sensor_id,
            timestamp_utc=_parse_datetime(timestamp_object["utc"], "measurement time"),
            value=float(value),
            unit=unit,
            latitude=float(coordinates["latitude"]),
            longitude=float(coordinates["longitude"]),
            has_flags=bool(result.get("flagInfo", {}).get("hasFlags", False)),
            period_label=str(period["label"]) if period.get("label") else None,
        )
    except OpenAQResponseError:
        raise
    except (KeyError, TypeError, ValueError) as error:
        raise OpenAQResponseError("invalid PM2.5 measurement response object") from error


class OpenAQClient:
    """Small standard-library client for the OpenAQ v3 endpoints we use."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = OPENAQ_BASE_URL,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAQ_API_KEY")
        if not self.api_key:
            raise OpenAQAuthenticationError(
                "OPENAQ_API_KEY is required; set it in the environment or pass api_key"
            )
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        query = urlencode(params or {})
        url = f"{self.base_url}/{path.lstrip('/')}"
        if query:
            url = f"{url}?{query}"
        request = Request(
            url,
            headers={"X-API-Key": self.api_key, "Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
        except HTTPError as error:
            if error.code in {401, 403}:
                raise OpenAQAuthenticationError(
                    f"OpenAQ rejected the API key with HTTP {error.code}"
                ) from error
            raise OpenAQError(f"OpenAQ request failed with HTTP {error.code}") from error
        except URLError as error:
            raise OpenAQError(f"OpenAQ request failed: {error.reason}") from error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise OpenAQResponseError("OpenAQ returned invalid JSON") from error

        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise OpenAQResponseError("OpenAQ response must contain a results list")
        if payload.get("meta") is not None and not isinstance(payload["meta"], dict):
            raise OpenAQResponseError("OpenAQ response meta must be an object")
        return payload

    def sensors_for_location(self, station_id: int) -> list[SensorMetadata]:
        """Return all sensors reported for one OpenAQ location."""
        payload = self._get(f"locations/{station_id}/sensors")
        return [parse_sensor(result, station_id) for result in payload["results"]]

    def pm25_sensors_for_location(self, station_id: int) -> list[SensorMetadata]:
        """Return only sensors whose OpenAQ parameter name is PM2.5."""
        return [
            sensor for sensor in self.sensors_for_location(station_id) if sensor.is_pm25
        ]

    def measurements(
        self,
        sensor: SensorMetadata,
        *,
        datetime_from: datetime | None = None,
        datetime_to: datetime | None = None,
        limit: int = 100,
        max_pages: int = 100,
    ) -> list[PM25Observation]:
        """Fetch paginated raw measurements for one PM2.5 sensor."""
        if not sensor.is_pm25:
            raise ValueError(f"sensor {sensor.sensor_id} does not measure PM2.5")
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000")
        if max_pages < 1:
            raise ValueError("max_pages must be positive")
        for name, value in (("datetime_from", datetime_from), ("datetime_to", datetime_to)):
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} must include timezone information")
        if datetime_from and datetime_to and datetime_from > datetime_to:
            raise ValueError("datetime_from cannot be later than datetime_to")

        base_params: dict[str, Any] = {"limit": limit}
        if datetime_from:
            base_params["datetime_from"] = datetime_from.isoformat()
        if datetime_to:
            base_params["datetime_to"] = datetime_to.isoformat()

        observations: list[PM25Observation] = []
        for page in range(1, max_pages + 1):
            payload = self._get(
                f"sensors/{sensor.sensor_id}/measurements",
                {**base_params, "page": page},
            )
            results = payload["results"]
            observations.extend(parse_pm25_observation(item, sensor) for item in results)

            found = payload.get("meta", {}).get("found")
            if not results or len(results) < limit:
                break
            if found is not None and page * limit >= int(found):
                break
        else:
            raise OpenAQResponseError(
                f"pagination exceeded max_pages={max_pages} for sensor {sensor.sensor_id}"
            )

        return observations
