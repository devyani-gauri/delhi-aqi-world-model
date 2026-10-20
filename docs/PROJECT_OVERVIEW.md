# Project overview

## Vision

The Delhi AQI World Model aims to become a computational representation of
Delhi's air-quality system. It should combine observations, geography,
emissions, weather, and simulation so users can explore pollution hotspots,
forecast conditions, and compare interventions before deploying them.

Potential questions include:

- Where and when does PM2.5 accumulate?
- How do roads, traffic, buildings, and weather influence exposure?
- What could traffic restrictions or emission reductions change?
- Which interventions offer the strongest improvement under constraints?

## Current scope

The first study area is a 5 km × 5 km square centered on Connaught Place at
latitude 28.6315 and longitude 77.2167. It is represented as a 10 × 10 grid, so
each cell is approximately 500 m × 500 m. One step represents one hour and the
default run covers 24 hours.

The model state is a NumPy array shaped `(hours, rows, columns)`, currently
`(24, 10, 10)`. Each value represents modeled PM2.5 concentration in `µg/m³` for
one place and hour.

## What is real now

- Connaught Place center and derived geographic bounds
- OpenStreetMap road geometry from the Overpass API
- OpenAQ station IDs, names, coordinates, and parameter metadata
- Filtering for PM2.5-capable stations inside the study area

## What is synthetic now

- Uniform starting PM2.5 background
- Central hotspot and abstract traffic corridors
- Morning and evening traffic peaks
- Neighbor-based diffusion and fixed north-east advection
- Linear removal and seeded weather variation

## Current outputs

- Full hourly PM2.5 history as a NumPy file
- Selected-hour and multi-hour heatmaps
- OSM roads, monitoring sites, and grid on one context map
- An interactive Jupyter walkthrough with maps and time-series charts

## Scientific status

This is a software and modeling prototype. It is not calibrated or validated
against observations and must not be presented as an operational forecast.

It does not yet include actual timestamped PM2.5 readings in the model state,
measured traffic or emissions, real weather, building-aware flow, calibrated
parameters, forecast validation, uncertainty estimates, or an explicit
PM2.5-to-AQI conversion standard.

## Intended system

```text
Observations + geography + emissions + weather
                       ↓
              Calibrated world state
                       ↓
           Forecast and scenario simulator
                       ↓
             Intervention evaluation
                       ↓
          Optimization and policy support
```

Each new layer should be tested and visually inspectable before it is used by
higher-level optimization or agent workflows.
