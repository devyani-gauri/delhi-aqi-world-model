# Delhi AQI Project

## Overview  
The **Delhi AQI Project** aims to model and simulate air quality dynamics across New Delhi. Using open geospatial and air quality datasets, the project integrates traffic, building, and congestion models with agent-based and reinforcement learning (RL) systems. The end goal is to design and test intervention strategies to reduce AQI hotspots.

---

## Tech Stack  
- **Data & GIS:** OSMnx, OpenAQ, AIRDELHI, DPCC
- **Simulation:** FiPy (dispersion PDEs), Mesa (agent-based models)  
- **Visualization:** PyVista (3D) 
- **Agents & AI:** LangGraph (LLM planners), RLlib + PettingZoo (multi-agent RL)  
- **Optimization & Causal Tools:** OR-Tools, DoWhy/EconML, PyMC  

---

## Steps  

### 1. Data Ingestion and Processing  
1. Get data from **OSM (OpenStreetMap)** for New Delhi  
2. Visualize in **2D or 3D** (PyVista for 3D)  
3. Get **AQI data** from OpenAQ, AIRDELHI, DPCC  
4. Clean and merge data → generate **geolocated hotspot maps**  

### 2. Simulation Inputs  
- Add **traffic, building, congestion models** using Mesa  

### 3. Forecasting  
- Create an **AQI forecast** based on historical hotspot data  

### 4. Agent Creation  
1. **LLM-based tool planners** (LangGraph)  
2. **RL-based execution & evaluation agents** (RLlib + PettingZoo)  

---

## Roadmap (Future Work)  
- Integrate optimization (OR-Tools) for scheduling interventions  
- Add Bayesian calibration (PyMC) for emissions  
- Build dashboards for policymakers and city planners  
- Extend to **multi-scale modeling** (ward → city → NCR)  

---