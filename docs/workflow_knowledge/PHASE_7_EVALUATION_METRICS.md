# PHASE 7: EVALUATION METRICS

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 7 provides **research-grade metrics** to evaluate the quality and consistency of lighting decisions. It is purely observational.

### What Problem It Solves
How do we know if the lighting system is working well?
- Are decisions consistent across runs?
- Is the LLM producing stable outputs?
- Are we using the full range of lighting options?

Phase 7 answers these questions with quantifiable metrics.

### What Question It Answers
> "How good is our lighting system?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_7/`

```
phase_7/
├── __init__.py               # Module exports
├── README.md                 # Phase documentation
├── demo.py                   # Demo script
├── metrics.py                # Unified metrics engine
├── schemas.py                # Metric output schemas
├── trace_logger.py           # Execution trace logging
├── evaluation/
│   ├── __init__.py
│   ├── consistency.py        # Jaccard, determinism, drift
│   ├── coverage.py           # Group coverage, diversity
│   └── stability.py          # Cross-run stability
└── experiment_configs/
    ├── ablation.yaml         # Ablation study config
    └── baseline.yaml         # Baseline experiment config
```

---

### File: `phase_7/__init__.py`

**Exports:**
- `MetricsEngine` (from `metrics.py`)
- Evaluation functions

---

### File: `phase_7/metrics.py`

**Why This File Exists:**
Unified interface to all metrics. Contains `MetricsEngine` class.

---

### File: `phase_7/trace_logger.py`

**Why This File Exists:**
Logs execution traces for debugging and analysis.

---

### File: `phase_7/evaluation/consistency.py`

**Why This File Exists:**
Measures how consistent lighting decisions are.

**Key Functions:**
- `compute_jaccard_similarity(set_a, set_b)` — Group overlap
- `compute_determinism_score(instr_a, instr_b)` — Structural similarity
- `compute_drift_score(instructions)` — Sequence stability

---

### File: `phase_7/evaluation/coverage.py`

**Why This File Exists:**
Detects trivial solutions (using only one group, constant intensity).

**Key Functions:**
- `compute_group_coverage(instruction, available_groups)` — Utilization ratio
- `compute_parameter_diversity(instruction)` — Parameter variety

---

### File: `phase_7/evaluation/stability.py`

**Why This File Exists:**
Measures cross-run consistency for LLM outputs.

**Key Functions:**
- `compute_cross_run_stability(runs)` — How stable are outputs across runs?
- `compute_pairwise_stability(runs)` — Pairwise comparison

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

### Class: `MetricsEngine`

**Purpose:**
Unified interface for computing all metrics.

**Constructor:**
```python
def __init__(self, available_groups: Optional[Set[str]] = None):
```

**Internal State:**
- `self.available_groups`: Set of known group IDs for coverage calculation

**Key Methods:**
- `evaluate_instruction(instruction)` → coverage + diversity
- `evaluate_pair(instr_a, instr_b)` → determinism score
- `evaluate_sequence(instructions)` → drift score
- `evaluate_runs(runs)` → cross-run stability
- `generate_report(instructions, runs)` → comprehensive report

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `consistency.compute_jaccard_similarity(set_a, set_b) -> float`

**Exact Responsibility:**
Compute Jaccard similarity: |A ∩ B| / |A ∪ B|

**Returns:** 0.0 (no overlap) to 1.0 (identical)

---

### `consistency.compute_determinism_score(instr_a, instr_b, epsilon) -> Tuple[float, dict]`

**Exact Responsibility:**
Measure structural similarity between two instructions.

**Definition of "Determinism":**
- Same group_ids selected
- Same transition types
- Intensity within ε = ±0.05

**Returns:** 
- Score (0-1)
- Breakdown dict with sub-scores

---

### `consistency.compute_drift_score(instructions) -> float`

**Exact Responsibility:**
Measure how much lighting changes between consecutive scenes.

**Returns:** Average drift (0 = stable, 1 = completely different each time)

---

### `coverage.compute_group_coverage(instruction, available_groups) -> float`

**Exact Responsibility:**
What fraction of available groups are used?

**Returns:** 0.0 (none) to 1.0 (all)

---

### `coverage.compute_parameter_diversity(instruction) -> dict`

**Exact Responsibility:**
Measure variety in lighting parameters.

**Returns:**
```python
{
    "intensity_range": float,      # max - min intensity
    "transition_types": int,       # unique transition types
    "colors_used": int,            # unique colors
    "groups_used": int             # total groups
}
```

---

### `stability.compute_cross_run_stability(runs, epsilon) -> dict`

**Exact Responsibility:**
How consistent are results across multiple pipeline runs?

**Input:** List of runs, each run is a list of LightingInstructions

**Returns:**
```python
{
    "stability_score": float,  # 0-1
    "num_runs": int,
    "epsilon": float
}
```

---

### `MetricsEngine.generate_report(instructions, runs) -> dict`

**Exact Responsibility:**
Generate comprehensive metrics report.

**Output:**
```python
{
    "summary": {
        "num_instructions": int,
        "available_groups": int
    },
    "sequence_metrics": {
        "drift_score": float,
        "num_instructions": int
    },
    "instruction_metrics": [
        {
            "index": int,
            "scene_id": str,
            "coverage": float,
            "diversity": dict
        }
    ],
    "stability_metrics": dict  # if runs provided
}
```

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 7 EXECUTION FLOW                                         │
└─────────────────────────────────────────────────────────────────┘

1. INPUT: List of LightingInstruction from Phase 4
          │
          ▼
2. MetricsEngine instantiation
   └── Configure available_groups
          │
          ▼
3. Evaluate each instruction:
   ├── compute_group_coverage()
   └── compute_parameter_diversity()
          │
          ▼
4. Evaluate sequence:
   └── compute_drift_score()
          │
          ▼
5. If multiple runs provided:
   └── compute_cross_run_stability()
          │
          ▼
6. OUTPUT: Comprehensive metrics report
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Input: LightingInstruction
Same structure as Phase 4 output.

### Output: Metrics Report
```python
{
    "summary": {...},
    "sequence_metrics": {...},
    "instruction_metrics": [...],
    "stability_metrics": {...}  # optional
}
```

---

## 7️⃣ FAILURE BEHAVIOR

### Empty Instruction List
- Returns empty report
- **Continues**

### Single Instruction (No Sequence)
- Drift score = 0.0
- **Continues**

### Single Run (No Stability)
- Stability score = 1.0
- **Continues**

**Phase 7 cannot fail the pipeline.**

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 7 MUST NOT Do:
- ❌ Must NOT modify LightingInstructions
- ❌ Must NOT influence execution
- ❌ Must NOT control lighting (that's Phase 8)
- ❌ Must NOT make decisions (that's Phase 4)

### What Phase 7 MUST Do:
- ✅ Observe outputs without modification
- ✅ Compute reproducible metrics
- ✅ Provide actionable insights

### Principle: OBSERVATION ≠ CONTROL
Phase 7 measures. It doesn't change anything.

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why is determinism defined structurally, not bytewise?"

LLM outputs vary slightly in formatting.
Structural determinism compares:
- Same groups selected
- Intensity within tolerance
- Same transition types

This is fair, reproducible, and defensible in research papers.

### "Why is epsilon = 0.05 for intensity?"

5% tolerance accounts for:
- LLM randomness
- Floating point precision
- Negligible perceptual difference

### "Why does drift use 1 - similarity instead of raw difference?"

Drift should be high when things change a lot.
1 - similarity gives: 0 = stable, 1 = maximum change.

### "Why are there experiment configs in YAML?"

For research: ablation studies, baseline comparisons.
YAML is human-readable and version-controllable.

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 7:
1. **Non-invasive**: Never modifies input
2. **Reproducible**: Same inputs → same metrics
3. **Comprehensive**: Coverage, consistency, stability

### Invariants Maintained:
- All scores are in [0, 1]
- Reports are JSON-serializable
- No side effects

### What Would Break If Phase 7 Were Removed:
- No quality metrics
- No way to evaluate system performance
- No research validation
- Debugging becomes harder
