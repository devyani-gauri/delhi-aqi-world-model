# Core concepts

## PM2.5 and AQI

PM2.5 is particulate matter with an aerodynamic diameter around 2.5 micrometres
or less. Concentration is commonly expressed in `µg/m³`.

AQI is a dimensionless index derived from pollutant concentration using
jurisdiction-specific breakpoints. This project currently models synthetic
PM2.5 concentration, not AQI. Conversion should be a separate step after a
standard is selected.

## Grid cells and state

A grid cell represents an area, not a sensor. The current area contains 100
cells, each approximately 500 m × 500 m. Values are stored as:

```text
history[hour, row, column]
```

Higher resolution increases computational and data needs; it does not
automatically increase accuracy.

## Observations and interpolation

Monitoring stations provide sparse point measurements. The model needs a value
for every cell, so interpolation estimates unobserved locations. Interpolated
values are estimates, not new ground truth; method, distance scale, coverage,
quality, and uncertainty must be documented.

## Emissions, concentration, and exposure

- **Emissions:** pollutant mass released by sources over time
- **Concentration:** pollutant present in a volume of air
- **Exposure:** concentration combined with where people are and for how long

The current traffic layer behaves like a synthetic emission source, while grid
values are labeled concentration. A calibrated model needs consistent units and
documented conversion assumptions.

## Diffusion and advection

- **Diffusion** spreads concentration toward neighboring cells.
- **Advection** transports concentration with wind.

The prototype blends four neighbors and shifts a fraction north-east. These are
teaching rules, not a validated atmospheric solver.

## Initial and boundary conditions

The initial condition defines the first grid. The prototype starts every cell at
`45 µg/m³`; the next milestone will derive it from observations.

NumPy `roll` currently wraps values from one edge to the opposite edge, creating
periodic boundaries. This is convenient but geographically unrealistic and must
be replaced before scientific use.

## Calibration, validation, and reproducibility

Calibration estimates parameters from observations. Validation evaluates
predictions on data not used for fitting. A plausible map is not evidence of
accuracy; future work requires time-based splits, baselines, error metrics, and
uncertainty.

The fixed random seed makes synthetic runs repeatable. Cached OSM data prevents
map geometry from silently changing between runs.

## 2D and 3D

Matplotlib is the scientific validation view for cell indexing, station
placement, interpolation, and color scales. PyVista remains the intended 3D
presentation layer once the numerical field is validated. A 3D visualization
should display model results, not substitute for validating them.

## Agents and optimization

Agent-based, reinforcement-learning, and LLM planning components are future
layers for interventions. They should consume a validated simulation; they
cannot compensate for missing or uncalibrated physical inputs.
