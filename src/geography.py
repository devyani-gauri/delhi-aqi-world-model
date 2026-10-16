"""Real geographic context for the Connaught Place simulation grid."""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .model import SimulationConfig


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@dataclass(frozen=True, slots=True)
class GeographicBounds:
    south: float
    west: float
    north: float
    east: float

    def contains(self, latitude: float, longitude: float) -> bool:
        return self.south <= latitude <= self.north and self.west <= longitude <= self.east


@dataclass(frozen=True, slots=True)
class MonitoringStation:
    station_id: int
    name: str
    latitude: float
    longitude: float
    parameters: tuple[str, ...]


def group_station_sites(
    stations: list[MonitoringStation],
) -> list[tuple[str, float, float, int]]:
    """Collapse duplicate provider records into named physical sites for display."""
    grouped: dict[str, list[MonitoringStation]] = {}
    for station in stations:
        site_name = station.name.split(",", maxsplit=1)[0].strip()
        grouped.setdefault(site_name, []).append(station)

    return [
        (
            name,
            sum(station.latitude for station in records) / len(records),
            sum(station.longitude for station in records) / len(records),
            len(records),
        )
        for name, records in grouped.items()
    ]


def bounds_from_config(config: SimulationConfig) -> GeographicBounds:
    """Convert the square kilometre study area to latitude/longitude bounds."""
    half_size_km = config.area_size_km / 2.0
    latitude_delta = half_size_km / 111.32
    longitude_delta = half_size_km / (
        111.32 * math.cos(math.radians(config.center_lat))
    )
    return GeographicBounds(
        south=config.center_lat - latitude_delta,
        west=config.center_lon - longitude_delta,
        north=config.center_lat + latitude_delta,
        east=config.center_lon + longitude_delta,
    )


def load_pm25_stations(
    csv_path: str | Path, bounds: GeographicBounds
) -> list[MonitoringStation]:
    """Load PM2.5-capable monitoring stations inside the study area."""
    stations: list[MonitoringStation] = []
    with Path(csv_path).open(newline="", encoding="utf-8") as station_file:
        for row in csv.DictReader(station_file):
            parameters = tuple(
                parameter.strip().lower()
                for parameter in row["parameters"].split(",")
                if parameter.strip()
            )
            latitude = float(row["lat"])
            longitude = float(row["lon"])
            if "pm25" in parameters and bounds.contains(latitude, longitude):
                stations.append(
                    MonitoringStation(
                        station_id=int(row["id"]),
                        name=row["name"],
                        latitude=latitude,
                        longitude=longitude,
                        parameters=parameters,
                    )
                )
    return stations


def overpass_query(bounds: GeographicBounds) -> str:
    """Build a query for drivable roads with full node geometry."""
    bbox = f"{bounds.south},{bounds.west},{bounds.north},{bounds.east}"
    return (
        "[out:json][timeout:60];"
        f'way["highway"]["highway"!="footway"]["highway"!="path"]({bbox});'
        "out tags geom;"
    )


def download_osm_roads(
    bounds: GeographicBounds,
    output_path: str | Path,
    endpoint: str = OVERPASS_URL,
) -> Path:
    """Download an OSM road snapshot from the public Overpass API."""
    request = Request(
        endpoint,
        data=urlencode({"data": overpass_query(bounds)}).encode("utf-8"),
        headers={"User-Agent": "delhi-aqi-world-model/0.1"},
    )
    with urlopen(request, timeout=90) as response:
        payload = json.load(response)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    return path


def load_road_segments(json_path: str | Path) -> list[tuple[list[float], list[float], str]]:
    """Extract longitude/latitude polylines and road classes from Overpass JSON."""
    payload: dict[str, Any] = json.loads(Path(json_path).read_text(encoding="utf-8"))
    segments: list[tuple[list[float], list[float], str]] = []
    for element in payload.get("elements", []):
        geometry = element.get("geometry", [])
        if len(geometry) < 2:
            continue
        longitudes = [float(node["lon"]) for node in geometry]
        latitudes = [float(node["lat"]) for node in geometry]
        road_class = element.get("tags", {}).get("highway", "unclassified")
        segments.append((longitudes, latitudes, road_class))
    return segments


def plot_context_map(
    road_segments: list[tuple[list[float], list[float], str]],
    stations: list[MonitoringStation],
    config: SimulationConfig,
) -> Figure:
    """Plot real roads and monitors beneath the simulation grid."""
    bounds = bounds_from_config(config)
    figure, axis = plt.subplots(figsize=(9, 9))
    major_classes = {"motorway", "trunk", "primary", "secondary"}
    station_sites = group_station_sites(stations)

    for longitudes, latitudes, road_class in road_segments:
        is_major = road_class in major_classes
        axis.plot(
            longitudes,
            latitudes,
            color="#5f6368" if is_major else "#b9bec4",
            linewidth=1.1 if is_major else 0.45,
            alpha=0.85 if is_major else 0.62,
            zorder=1,
        )

    for index in range(config.grid_size + 1):
        fraction = index / config.grid_size
        longitude = bounds.west + fraction * (bounds.east - bounds.west)
        latitude = bounds.south + fraction * (bounds.north - bounds.south)
        axis.axvline(longitude, color="#2878b5", linewidth=0.45, alpha=0.55, zorder=2)
        axis.axhline(latitude, color="#2878b5", linewidth=0.45, alpha=0.55, zorder=2)

    if station_sites:
        axis.scatter(
            [longitude for _, _, longitude, _ in station_sites],
            [latitude for _, latitude, _, _ in station_sites],
            marker="o",
            s=54,
            color="#d62728",
            edgecolor="white",
            linewidth=0.8,
            label="OpenAQ PM2.5 station",
            zorder=4,
        )
        for name, latitude, longitude, record_count in station_sites:
            label = f"{name} ({record_count})" if record_count > 1 else name
            on_right = longitude > config.center_lon
            axis.annotate(
                label,
                (longitude, latitude),
                xytext=(-6 if on_right else 6, 6),
                textcoords="offset points",
                horizontalalignment="right" if on_right else "left",
                fontsize=7,
                zorder=5,
            )

    axis.scatter(
        [config.center_lon],
        [config.center_lat],
        marker="*",
        s=130,
        color="#ffbf00",
        edgecolor="#333333",
        linewidth=0.8,
        label="Connaught Place center",
        zorder=5,
    )
    axis.set(
        xlim=(bounds.west, bounds.east),
        ylim=(bounds.south, bounds.north),
        xlabel="Longitude",
        ylabel="Latitude",
        title="Connaught Place PM2.5 simulation geography",
        aspect="equal",
    )
    axis.legend(loc="lower left", fontsize=8)
    axis.grid(False)
    figure.tight_layout()
    return figure


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the real geography context map")
    parser.add_argument("--stations", type=Path, default=Path("data/delhi_stations.csv"))
    parser.add_argument(
        "--roads", type=Path, default=Path("data/connaught_place_roads.json")
    )
    parser.add_argument("--output", type=Path, default=Path("outputs/context_map.png"))
    parser.add_argument("--refresh-roads", action="store_true")
    args = parser.parse_args()

    config = SimulationConfig()
    bounds = bounds_from_config(config)
    if args.refresh_roads or not args.roads.exists():
        download_osm_roads(bounds, args.roads)

    stations = load_pm25_stations(args.stations, bounds)
    roads = load_road_segments(args.roads)
    figure = plot_context_map(roads, stations, config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180)
    plt.close(figure)
    site_count = len(group_station_sites(stations))
    print(
        f"Mapped {len(roads)} OSM road segments and "
        f"{len(stations)} PM2.5 records across {site_count} sites"
    )
    print(f"Saved context map to {args.output}")


if __name__ == "__main__":
    main()
