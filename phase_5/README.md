# Phase 5 — Simulation & Visualization

> Reflects `baseline-rule-engine-stable` tag. Last updated: 2026-02-18.

## Purpose

Phase 5 renders lighting instructions into a **High-Fidelity 3D Simulation**. 
It acts as a **bridge** to the **External Simulation Prototype**, translating abstract Phase 4 instructions into physical fixture commands and launching the sophisticated Three.js visualization.

## Components

| File | Component | Description |
|------|-----------|-------------|
| `server.py` | `SimulationLauncher` | Exports data & launches the External Prototype (WebSocket Backend + HTTP Frontend) |
| `threejs_adapter.py` | `InstructionExporter` | Translates Phase 4 data (groups, semantic colors) to Prototype format |
| `playback_engine.py` | `PlaybackEngine` | *Legacy compatibility for Phase 6 pipeline* |
| `scene_renderer.py` | `SceneRenderer` | *Legacy compatibility* |
| `color_utils.py` | Color utilities | Used by Exporter for semantic color resolution |
| `__init__.py` | Module exports | Exposes `launch_simulation` |

## Inputs / Outputs

- **Input**: `List[LightingInstruction]` dicts from Phase 4
- **Output**: 
    - JSON file export to `external_prototype/data/lighting_instructions.json`
    - Live 3D Simulation via External Prototype (localhost:8081)

## How to Run

```bash
conda activate venv_ALG_311
cd Automated_Auditorium_Lighting
python -m phase_5.server
```

This will:
1. Export instructions (defaults to a demo script if none provided)
2. Start the **External Prototype Backend** (WebSocket on port 8765)
3. Start the **Visual Frontend** (HTTP on port 8081)

## Boundaries

- Phase 5 does **NOT** contain the simulation logic itself (that lives in `external_prototype/`)
- Phase 5 does **NOT** modify lighting instructions (only translates format)
- Phase 5 does **NOT** call LLMs

## Failure Handling

Phase 5 is **OPTIONAL**. If the external prototype cannot be launched (e.g., missing files), it logs a warning and the pipeline continues without visualization.
