"""Command-line entry point for the first PM2.5 simulation milestone."""

import argparse
from pathlib import Path

import numpy as np

from .model import SimulationConfig, simulate_pm25
from .utils import save_hour


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Delhi PM2.5 grid prototype")
    parser.add_argument("--hour", type=int, default=19, help="hour to render (default: 19)")
    parser.add_argument(
        "--output-dir", type=Path, default=Path("outputs"), help="output directory"
    )
    args = parser.parse_args()

    config = SimulationConfig()
    history = simulate_pm25(config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    np.save(args.output_dir / "pm25_history.npy", history)
    image_path = save_hour(history, args.hour, config, args.output_dir / "pm25_map.png")

    print(f"Simulated {config.hours} hours across {config.cell_count} cells")
    print(f"Concentration range: {history.min():.1f}–{history.max():.1f} µg/m³")
    print(f"Saved map to {image_path}")


if __name__ == "__main__":
    main()
