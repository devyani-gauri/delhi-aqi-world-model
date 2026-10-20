# Architecture

## Principles

- Separate geographic data from pollution dynamics.
- Keep reusable logic in `src/`; use notebooks for exploration and explanation.
- Make runs reproducible through explicit configuration and random seeds.
- Distinguish observed inputs from assumptions and synthetic values.
- Validate in 2D before adding 3D presentation or intelligent agents.

## Current data flow

```text
SimulationConfig
   ├── bounds_from_config ──→ geographic bounds
   │                            ├── cached OSM roads
   │                            └── OpenAQ station metadata
   │                                      ↓
   │                              geographic context map
   │
   └── simulate_pm25 ───────→ hourly NumPy grid history
                                      ↓
                               heatmaps and charts
```

Geography and simulation share configuration, but real roads and station
measurements do not yet drive the numerical model.

## Modules

### `src/model.py`

- `SimulationConfig`: spatial, temporal, and reproducibility assumptions
- `_traffic_source`: synthetic spatial emissions
- `_traffic_multiplier`: morning and evening peaks
- `_disperse`: simplified diffusion and north-east advection
- `simulate_pm25`: hourly transition loop returning `(hours, rows, columns)`

### `src/geography.py`

- Converts the kilometre study area to latitude/longitude bounds
- Loads and filters PM2.5-capable OpenAQ station metadata
- Groups duplicate provider records for display
- Downloads and parses OSM roads through Overpass
- Draws roads, sites, grid, and Connaught Place center

### `src/utils.py`

Creates and saves stable-scale hourly PM2.5 heatmaps. Matplotlib uses inline
rendering in Jupyter and the headless `Agg` backend in scripts.

### `src/server.py`

The simulation CLI creates configuration, runs the model, saves the complete
history, and renders a selected hour.

### `tests/`

Tests cover configuration validation, grid output, reproducibility, geographic
bounds, station filtering and grouping, and OSM parsing.

## Notebooks

| Notebook | Role |
|---|---|
| `3d_model.ipynb` | Historical OSM building/street and PyVista experiment |
| `aqi_ingestion.ipynb` | OpenAQ station inventory exploration |
| `project_walkthrough.ipynb` | Maintained interactive technical walkthrough |

Reusable logic should not live only in notebooks.

## Next architecture boundary

```text
Timestamped PM2.5 readings
          ↓
Validation and unit normalization
          ↓
Station-to-grid assignment
          ↓
Spatial interpolation with uncertainty
          ↓
Observed initial grid for simulate_pm25
```

Later layers can introduce road-derived emissions, weather forcing,
calibration, forecast validation, and PyVista without combining all
responsibilities in one module.
