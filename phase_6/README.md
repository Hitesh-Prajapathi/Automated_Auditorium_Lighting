# Phase 6: Orchestration & Pipeline Control

## Purpose

Phase 6 is the **ORCHESTRATION SPINE** of the Automated Auditorium Lighting system.

It:
- Controls execution order
- Enables/disables phases
- Passes data between phases
- Tracks execution state
- Handles failures deterministically

It **DOES NOT**:
- Make lighting decisions
- Interpret emotions
- Render visuals
- Compute metrics
- Talk to hardware
- Fix or modify outputs of other phases

---

## Files

| File | Purpose |
|------|---------|
| `config_models.py` | Configuration and result models |
| `errors.py` | Deterministic error definitions |
| `state_tracker.py` | Queryable execution state |
| `pipeline_runner.py` | Main orchestration logic |
| `batch_executor.py` | Multi-script batch execution |

---

## Canonical Pipeline Order (LOCKED)

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 7 → Phase 8
 (REQ)    (OPT)     (REQ)     (REQ)    (OPT)    (OPT)    (FUTURE)
```

---

## Failure Handling

| Phase | Failure Behavior |
|-------|------------------|
| Phase 1 | HARD FAIL |
| Phase 2 | Continue with emotion = null |
| Phase 3 | HARD FAIL |
| Phase 4 | Allow fallback, then HARD FAIL |
| Phase 5 | NON-FATAL, log & continue |
| Phase 7 | NON-FATAL, log & continue |
| Phase 8 | NOT IMPLEMENTED |

---

## Usage

### Single Script

```python
from phase_6 import PipelineRunner, PipelineConfig

config = PipelineConfig(
    enable_phase_5=True,
    enable_phase_7=False,
    use_llm=False
)

runner = PipelineRunner(config)
result = runner.run("data/raw_scripts/Script-1.txt")

print(result.final_status)
```

### Batch Execution

```python
from phase_6 import BatchExecutor, PipelineConfig

config = PipelineConfig(enable_phase_5=False)
executor = BatchExecutor(config)

results = executor.run_directory("data/raw_scripts/", pattern="*.txt")
summary = executor.summarize_results(results)

print(f"Success rate: {summary['success_rate']:.0%}")
```

---

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_phase_5` | bool | True | Enable visualization |
| `enable_phase_7` | bool | True | Enable evaluation |
| `enable_phase_8` | bool | False | Enable hardware (future) |
| `demo_mode` | bool | False | Demo execution mode |
| `use_llm` | bool | False | Pass-through to Phase 4 |

---

## State Tracking

Query execution state at any time:

```python
runner = PipelineRunner(config)
# ... during execution ...
state = runner.get_state()
print(f"Current phase: {state.current_phase}")
print(f"Scenes processed: {state.current_scene_index}/{state.total_scenes}")
```

---

## Contract Enforcement

Phase 6 enforces **ONLY**:
- Scene schema before Phase 4
- LightingInstruction schema after Phase 4

Phase 6 does **NOT** validate:
- Visual correctness
- Artistic quality
- Metrics meaning

---

## Architecture Compliance

Phase 6 follows these rules:
- Treats every phase as a **BLACK BOX**
- ONLY calls published entry points
- NEVER modifies phase outputs
- NEVER retries silently
- NEVER swallows errors

**Phase 6 is orchestration-only and does not influence system decisions.**
