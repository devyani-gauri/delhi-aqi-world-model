import csv
import json
import tempfile
import unittest
from pathlib import Path

from src.geography import (
    GeographicBounds,
    bounds_from_config,
    group_station_sites,
    load_pm25_stations,
    load_road_segments,
    overpass_query,
)
from src.model import SimulationConfig


class GeographicBoundsTests(unittest.TestCase):
    def test_bounds_are_centered_on_config(self) -> None:
        config = SimulationConfig()
        bounds = bounds_from_config(config)
        self.assertAlmostEqual((bounds.north + bounds.south) / 2, config.center_lat)
        self.assertAlmostEqual((bounds.east + bounds.west) / 2, config.center_lon)
        self.assertTrue(bounds.contains(config.center_lat, config.center_lon))

    def test_query_includes_bounds_and_geometry(self) -> None:
        bounds = GeographicBounds(1.0, 2.0, 3.0, 4.0)
        query = overpass_query(bounds)
        self.assertIn("(1.0,2.0,3.0,4.0)", query)
        self.assertIn("out tags geom", query)


class GeographicDataTests(unittest.TestCase):
    def test_station_sites_group_provider_duplicates(self) -> None:
        from src.geography import MonitoringStation

        stations = [
            MonitoringStation(1, "ITO, Delhi - CPCB", 28.62, 77.24, ("pm25",)),
            MonitoringStation(2, "ITO, New Delhi - CPCB", 28.64, 77.22, ("pm25",)),
        ]
        sites = group_station_sites(stations)
        self.assertEqual(sites[0][0], "ITO")
        self.assertAlmostEqual(sites[0][1], 28.63)
        self.assertAlmostEqual(sites[0][2], 77.23)
        self.assertEqual(sites[0][3], 2)

    def test_station_loader_filters_by_bounds_and_pm25(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stations.csv"
            with path.open("w", newline="", encoding="utf-8") as station_file:
                writer = csv.DictWriter(
                    station_file, fieldnames=["id", "name", "lat", "lon", "parameters"]
                )
                writer.writeheader()
                writer.writerow(
                    {"id": 1, "name": "Inside", "lat": 2, "lon": 3, "parameters": "pm25, no2"}
                )
                writer.writerow(
                    {"id": 2, "name": "No PM", "lat": 2, "lon": 3, "parameters": "no2"}
                )
                writer.writerow(
                    {"id": 3, "name": "Outside", "lat": 8, "lon": 9, "parameters": "pm25"}
                )
            stations = load_pm25_stations(path, GeographicBounds(1, 2, 3, 4))
            self.assertEqual([station.name for station in stations], ["Inside"])

    def test_road_loader_extracts_geometry(self) -> None:
        payload = {
            "elements": [
                {
                    "type": "way",
                    "tags": {"highway": "primary"},
                    "geometry": [{"lat": 1, "lon": 2}, {"lat": 3, "lon": 4}],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "roads.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            self.assertEqual(load_road_segments(path), [([2.0, 4.0], [1.0, 3.0], "primary")])


if __name__ == "__main__":
    unittest.main()
