# Phase 7 — Evaluation & Metrics

> Reflects `baseline-rule-engine-stable` tag. Last updated: 2026-02-12.

## Purpose

Phase 7 observes and logs execution traces, then computes research-grade metrics for lighting decisions. It is fully removable without affecting system execution.

## Components

| File | Component | Description |
|------|-----------|-------------|
| `trace_logger.py` | `TraceLogger` | Logs input/output hashes per scene |
| `metrics.py` | `MetricsEngine` | Computes coverage, diversity, drift, determinism |
| `schemas.py` | `TraceEntry`, `TraceLog`, `RAGContextRef` | Pydantic trace models |
| `evaluation/consistency.py` | `compute_jaccard_similarity`, `compute_determinism_score`, `compute_drift_score`, `extract_group_ids` | Consistency metrics |
| `evaluation/coverage.py` | `compute_group_coverage`, `compute_parameter_diversity` | Coverage metrics |
| `evaluation/stability.py` | `compute_cross_run_stability` | Cross-run stability |

## Pipeline Integration

```python
# In pipeline_runner.py (_run_phase_7):
trace_logger = TraceLogger(output_dir="data/traces/", seed=42)
for scene, instruction in zip(scenes, instructions):
    trace_logger.log_decision(scene, instruction)
trace_logger.save()  # → data/traces/trace_<uuid>.json

metrics_engine = MetricsEngine(available_groups={"front_wash", "back_light", ...})
report = metrics_engine.generate_report(instructions)
```

## Baseline Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| Drift Score | 0.333 | Avg change between consecutive scenes (0=stable, 1=chaotic) |
| Coverage | 0.4 | Groups used / total (2 of 5) |
| Intensity Range | 0.075–0.24 | Per-scene intensity diversity |
| Transition Types | 1 | Only `fade` in baseline |
| Determinism | 1.0 | Same input → same output (guaranteed in rule-based mode) |

## Metric Definitions

- **Drift Score**: `avg(1 - Jaccard_similarity)` between consecutive scene instructions
- **Coverage**: `|groups_used| / |available_groups|`
- **Determinism**: Structural match: group IDs + intensity within ε=0.05 + transition type
- **Diversity**: Spread of intensity, transition types, and color count per scene

## Boundaries

Phase 7 is **OBSERVATIONAL ONLY**. It does NOT:
- Import from Phase 4 or other phases
- Call LLM APIs
- Modify lighting intent
- Influence execution

## Failure Handling

Phase 7 is **OPTIONAL** — non-fatal. If metrics fail, the pipeline logs a warning and continues.

## Output

Trace files saved to `data/traces/trace_<uuid>.json`:

```json
{
  "run_id": "a366f360-...",
  "created_at": "2026-02-12T...",
  "entries": [
    {
      "scene_id": "unknown",
      "input_hash": "abc123...",
      "output_hash": "def456...",
      "seed": 42
    }
  ]
}
```
