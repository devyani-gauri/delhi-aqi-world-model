# Development guide

## Requirements and setup

- Python 3.11 or newer
- Git
- Internet access only when refreshing OpenAQ or OpenStreetMap data

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,notebook]"
python -m pytest
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Dependencies

`pyproject.toml` is the source of truth.

| Group | Dependency | Purpose |
|---|---|---|
| Runtime | NumPy | Grid storage and numerical operations |
| Runtime | Matplotlib | 2D maps, heatmaps, and charts |
| `dev` | pytest | Automated testing |
| `notebook` | JupyterLab | Editable walkthrough and exploration |

Reusable modules currently use standard-library `csv`, `json`, `urllib`, and
`dataclasses` instead of additional GIS dependencies.

PyVista appears in the earlier 3D notebook but is not a declared dependency of
the runnable prototype. OSMnx, FiPy, Mesa, RLlib, PettingZoo, LangGraph,
OR-Tools, PyMC, DoWhy, and EconML are possible future tools, not current
requirements.

## Commands

```bash
# Tests
python -m pytest

# Default simulation; saves outputs/pm25_history.npy and outputs/pm25_map.png
python -m src.server

# Select an hour and output directory
python -m src.server --hour 9 --output-dir morning_run

# Context map using cached OSM data
python -m src.geography

# Refresh OSM roads, then render
python -m src.geography --refresh-roads

# Interactive walkthrough
python -m jupyter lab
```

## Data

| File | Origin | Contents |
|---|---|---|
| `data/delhi_stations.csv` | OpenAQ v3 | Station IDs, names, coordinates, parameters |
| `data/connaught_place_roads.json` | OSM Overpass | Cached highway ways and geometry |

The station CSV describes station capability and location, not historical PM2.5
measurements. Never commit API keys. The ingestion notebook reads
`OPENAQ_API_KEY` from the environment or a local ignored `.env` file.

Generated outputs, virtual environments, notebook checkpoints, test caches, and
package metadata are ignored and should be recreated rather than committed.

## Commit checklist

Each milestone commit should:

1. Include tests for changed behavior.
2. Pass `python -m pytest` and `git diff --check`.
3. Update documentation affected by the change.
4. Update status in `docs/ROADMAP.md`.
5. Exclude generated outputs, credentials, and local environments.

Completed milestone commits currently go directly to GitHub `main`.
