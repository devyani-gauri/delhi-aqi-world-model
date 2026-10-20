# Roadmap and task list

This is the living source of truth for project status. Update it in the same
commit that completes, adds, removes, or substantially changes a task.

- `[x]` completed and merged
- `[ ]` not completed

## Milestone 0 — Foundation (complete)

- [x] Establish repository structure and installable Python project
- [x] Add development and notebook dependencies
- [x] Add automated tests
- [x] Document setup and common commands
- [x] Add an interactive technical walkthrough

Exit criteria: a new contributor can install the project, run tests and CLIs,
and open the walkthrough from documented commands.

## Milestone 1 — Geographic prototype (complete)

- [x] Select Connaught Place as the initial study area
- [x] Define a 5 km × 5 km boundary and 10 × 10 grid
- [x] Download and cache OSM road geometry
- [x] Load the OpenAQ station inventory
- [x] Filter PM2.5-capable stations inside the boundary
- [x] Group duplicate provider records for display
- [x] Render roads, monitoring sites, grid, and center together

Exit criteria: the grid is visually verifiable against real roads and station
locations.

## Milestone 2 — Synthetic dynamics prototype (complete)

- [x] Represent state as `(hours, rows, columns)` NumPy data
- [x] Add synthetic traffic sources and rush-hour peaks
- [x] Add simplified diffusion, advection, removal, and seeded noise
- [x] Save simulation history and render maps/charts
- [x] Test dimensions, values, validation, and reproducibility

Exit criteria: a deterministic 24-hour demonstration runs end to end and its
state transitions are visually inspectable.

## Milestone 3 — Observed PM2.5 initialization (next)

- [ ] Define an observation schema: station, timestamp, value, unit, provenance
- [ ] Add a reusable OpenAQ client outside the notebook
- [ ] Fetch timestamped PM2.5 readings for study-area stations
- [ ] Cache a reproducible raw observation snapshot
- [ ] Validate timestamps, units, coordinates, and missing values
- [ ] Resolve duplicate sensor/provider records explicitly
- [ ] Assign each observation to a grid cell
- [ ] Select and document a spatial interpolation method
- [ ] Estimate an initial value and uncertainty for every grid cell
- [ ] Visualize measured points against the interpolated surface
- [ ] Test parsing, validation, cell assignment, and interpolation
- [ ] Allow `simulate_pm25` to accept an observed initial grid
- [ ] Update the walkthrough with the observation pipeline

Exit criteria: the model starts from a timestamped, traceable PM2.5 field
derived from real observations, with assumptions and missing coverage visible.

## Milestone 4 — Road-derived emissions

- [ ] Convert OSM road geometry into per-cell density features
- [ ] Preserve road classes and define documented class weights
- [ ] Replace abstract corridors with road-derived spatial sources
- [ ] Identify and ingest an appropriate traffic-volume dataset
- [ ] Separate road activity from emissions factors
- [ ] Define consistent emissions and concentration units
- [ ] Compare synthetic and road-derived source maps
- [ ] Add sensitivity tests

Exit criteria: spatial emissions derive from documented geographic and traffic
inputs rather than hand-drawn corridors.

## Milestone 5 — Weather and boundary physics

- [ ] Select and ingest weather data
- [ ] Replace fixed advection with time-varying wind
- [ ] Replace periodic edge wrapping with documented boundary conditions
- [ ] Evaluate whether FiPy or another PDE solver is appropriate
- [ ] Add mass-balance and numerical-stability checks

Exit criteria: transport responds to real weather, uses defensible boundaries,
and passes numerical sanity checks.

## Milestone 6 — Calibration and forecasting

- [ ] Assemble a historical modeling dataset
- [ ] Define persistence and statistical baselines
- [ ] Split calibration and validation periods without time leakage
- [ ] Choose spatial and temporal error metrics
- [ ] Calibrate uncertain parameters
- [ ] Quantify predictive uncertainty
- [ ] Document the supported forecast horizon
- [ ] Add PM2.5-to-AQI conversion after selecting a standard

Exit criteria: forecasts are evaluated out of sample against baselines and
reported with uncertainty.

## Milestone 7 — Buildings and PyVista world model

- [ ] Refactor useful 3D logic out of `3d_model.ipynb`
- [ ] Declare and document 3D dependencies
- [ ] Align the 2D grid with building and street geometry
- [ ] Decide whether buildings affect physics, visualization, or both
- [ ] Project hourly PM2.5 values onto a PyVista scene
- [ ] Add time controls or animation
- [ ] Verify the 3D view preserves the 2D values and scale

Exit criteria: validated model state is reproducibly explorable in 3D without
obscuring scientific assumptions.

## Milestone 8 — Interventions

- [ ] Define actions, constraints, and no-action baselines
- [ ] Define outcome, equity, cost, and feasibility metrics
- [ ] Add reproducible counterfactual scenario execution
- [ ] Determine whether Mesa adds value for traffic or behavioral agents

Exit criteria: users can configure and compare intervention scenarios using
documented metrics.

## Milestone 9 — Optimization and intelligent agents

- [ ] Define a stable environment API
- [ ] Establish non-agent optimization baselines
- [ ] Evaluate OR-Tools for constrained scheduling
- [ ] Evaluate PettingZoo/RLlib only for justified sequential decisions
- [ ] Evaluate LangGraph only for transparent tool orchestration
- [ ] Add safety constraints and audit trails
- [ ] Compare agents against simpler baselines

Exit criteria: advanced agents demonstrate measurable value over simpler methods
and operate only on validated model outputs.

## Cross-cutting backlog

- [ ] Select a software license
- [ ] Add continuous integration
- [ ] Add formatting, linting, and static type checking
- [ ] Add data provenance manifests with retrieval timestamps and licenses
- [ ] Define dataset and model-configuration versioning
- [ ] Add contributor guidelines and issue templates when collaboration expands
- [ ] Review privacy, public-health communication, and responsible-use risks
- [ ] Plan expansion from Connaught Place to ward, city, and NCR scales

## Documentation checklist for every milestone commit

- [ ] Does `README.md` still describe the current runnable project?
- [ ] Did setup or dependencies change in `DEVELOPMENT.md`?
- [ ] Did module boundaries or data flow change in `ARCHITECTURE.md`?
- [ ] Did assumptions or terminology change in `CONCEPTS.md`?
- [ ] Were completed and newly discovered tasks updated here?
- [ ] Does the walkthrough demonstrate the new behavior where appropriate?
