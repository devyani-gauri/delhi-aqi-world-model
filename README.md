# Delhi AQI World Model

An experimental, data-grounded world model for exploring how PM2.5 may be
distributed across Delhi and how pollution could respond to interventions.

The current prototype combines real OpenStreetMap roads and OpenAQ monitoring
station locations with a small synthetic grid simulation centered on Connaught
Place. It validates the project architecture and visualization workflow; it is
**not yet a calibrated forecast or public-health decision tool**.

## Current state

- 5 km × 5 km study area centered on Connaught Place
- 10 × 10 grid with hourly state updates over 24 hours
- 4,782 cached OpenStreetMap road segments
- PM2.5-capable OpenAQ station inventory and site grouping
- Typed PM2.5 observation records and a reusable OpenAQ v3 client
- Synthetic emissions, rush-hour peaks, dispersion, removal, and weather noise
- 2D maps, hourly comparisons, and an interactive Jupyter walkthrough
- 17 automated tests

See [Project overview](docs/PROJECT_OVERVIEW.md) for the full scope and current
limitations.

## Quick start

Python 3.11 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,notebook]"
python -m pytest
python -m jupyter lab
```

Open `notebooks/project_walkthrough.ipynb` and run cells in order with
**Shift+Enter**.

Run the simulation from the terminal:

```bash
python -m src.server
```

Generate the geographic context map from the cached road snapshot:

```bash
python -m src.geography
```

Refresh the road snapshot from OpenStreetMap first:

```bash
python -m src.geography --refresh-roads
```

Generated arrays and maps are written under `outputs/` and are not committed.

## Documentation

- [Project overview](docs/PROJECT_OVERVIEW.md) — purpose, scope, status, and limitations
- [Development guide](docs/DEVELOPMENT.md) — setup, dependencies, commands, and data
- [Architecture](docs/ARCHITECTURE.md) — modules, data flow, and design boundaries
- [Concepts](docs/CONCEPTS.md) — PM2.5, AQI, grids, observations, and dispersion
- [Roadmap and task list](docs/ROADMAP.md) — completed work, next milestones, and backlog

## Repository layout

```text
data/          Cached OpenAQ station inventory and OSM road snapshot
docs/          Living project documentation and roadmap
notebooks/     Exploration, ingestion, 3D experiments, and guided walkthrough
src/           Simulation, geography, observations, visualization, and CLI code
tests/         Automated unit tests
```

## Documentation policy

Each feature commit should update documentation when it changes behavior,
dependencies, architecture, assumptions, outputs, or roadmap status. Completed
tasks should be checked off in `docs/ROADMAP.md` in the same commit that delivers
them.

## License

No license has been selected yet. Until one is added, the repository is not
offered under an open-source license.
