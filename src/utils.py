"""Visualization helpers for model output."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray

from .model import SimulationConfig


def plot_hour(
    history: NDArray[np.float64],
    hour: int,
    config: SimulationConfig,
) -> Figure:
    """Plot one hourly concentration grid with a stable color scale."""
    if not 0 <= hour < history.shape[0]:
        raise IndexError(f"hour must be between 0 and {history.shape[0] - 1}")

    figure, axis = plt.subplots(figsize=(7, 6))
    image = axis.imshow(
        history[hour],
        origin="lower",
        cmap="magma_r",
        vmin=float(history.min()),
        vmax=float(history.max()),
        extent=(0, config.area_size_km, 0, config.area_size_km),
    )
    axis.set(
        title=f"Synthetic {config.pollutant} — hour {hour:02d}:00",
        xlabel="Distance east (km)",
        ylabel="Distance north (km)",
    )
    figure.colorbar(image, ax=axis, label="PM2.5 (µg/m³)")
    figure.tight_layout()
    return figure


def save_hour(
    history: NDArray[np.float64],
    hour: int,
    config: SimulationConfig,
    output_path: str | Path,
) -> Path:
    """Render one hourly grid to a PNG file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    figure = plot_hour(history, hour, config)
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return path
