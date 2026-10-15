"""Core grid model for the Delhi PM2.5 prototype.

This is a deliberately small, synthetic model. It is useful for testing the
simulation pipeline, but it is not a calibrated air-quality forecast.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


FloatGrid = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Spatial and temporal assumptions for one simulation run."""

    center_lat: float = 28.6315
    center_lon: float = 77.2167
    area_size_km: float = 5.0
    grid_size: int = 10
    hours: int = 24
    pollutant: str = "PM2.5"
    background_pm25: float = 45.0
    random_seed: int = 42

    def __post_init__(self) -> None:
        if self.area_size_km <= 0:
            raise ValueError("area_size_km must be positive")
        if self.grid_size < 3:
            raise ValueError("grid_size must be at least 3")
        if self.hours <= 0:
            raise ValueError("hours must be positive")
        if self.background_pm25 < 0:
            raise ValueError("background_pm25 cannot be negative")

    @property
    def cell_size_km(self) -> float:
        return self.area_size_km / self.grid_size

    @property
    def cell_count(self) -> int:
        return self.grid_size**2


def _traffic_source(grid_size: int) -> FloatGrid:
    """Create synthetic road corridors and a central traffic hotspot."""
    coordinates = np.linspace(-1.0, 1.0, grid_size)
    x, y = np.meshgrid(coordinates, coordinates)

    central_hotspot = 38.0 * np.exp(-((x / 0.28) ** 2 + (y / 0.28) ** 2))
    east_west_road = 17.0 * np.exp(-((y - 0.18) / 0.12) ** 2)
    north_south_road = 14.0 * np.exp(-((x + 0.25) / 0.10) ** 2)
    return central_hotspot + east_west_road + north_south_road


def _traffic_multiplier(hour: int) -> float:
    """Approximate morning and evening rush-hour emission peaks."""
    morning_peak = np.exp(-0.5 * ((hour - 9) / 2.0) ** 2)
    evening_peak = np.exp(-0.5 * ((hour - 19) / 2.2) ** 2)
    return float(0.30 + 0.75 * morning_peak + 0.95 * evening_peak)


def _disperse(grid: FloatGrid) -> FloatGrid:
    """Apply one simple diffusion/advection step with a north-east wind."""
    neighbor_mean = (
        np.roll(grid, 1, axis=0)
        + np.roll(grid, -1, axis=0)
        + np.roll(grid, 1, axis=1)
        + np.roll(grid, -1, axis=1)
    ) / 4.0
    diffused = 0.72 * grid + 0.28 * neighbor_mean
    advected = 0.88 * diffused + 0.12 * np.roll(diffused, (-1, 1), axis=(0, 1))
    return advected


def simulate_pm25(config: SimulationConfig = SimulationConfig()) -> FloatGrid:
    """Simulate hourly PM2.5 concentration in micrograms per cubic metre.

    Returns an array shaped ``(hours, grid_size, grid_size)``.
    """
    rng = np.random.default_rng(config.random_seed)
    source = _traffic_source(config.grid_size)
    current = np.full(
        (config.grid_size, config.grid_size), config.background_pm25, dtype=float
    )
    history = np.empty((config.hours, config.grid_size, config.grid_size), dtype=float)

    for hour in range(config.hours):
        current = _disperse(current)
        emissions = source * _traffic_multiplier(hour)
        removal = 0.08 * (current - config.background_pm25)
        weather_noise = rng.normal(0.0, 1.2, current.shape)
        current = np.clip(current + emissions - removal + weather_noise, 0.0, None)
        history[hour] = current

    return history
