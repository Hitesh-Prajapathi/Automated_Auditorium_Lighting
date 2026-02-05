# Phase 6: Orchestration & Pipeline Control

## Overview

Phase 6 is the **ORCHESTRATION SPINE** of the Automated Auditorium Lighting system. It controls execution order, manages phase enables/disables, and passes data between phases.

**Key principle:** Phase 6 is orchestration-only and does not influence system decisions.

---

## Architecture Position

```
      ┌─────────────────────────────────────────────────────────────┐
      │                    PHASE 6: ORCHESTRATION                   │
      │  Controls flow, does not modify data                        │
      └─────────────────────────────────────────────────────────────┘
                                    │
        ┌───────┬───────┬───────┬───┴───┬───────┬───────┬───────┐
        │   1   │   2   │   3   │   4   │   5   │   7   │   8   │
        │Parsing│Emotion│  RAG  │Decision│Simulate│Evaluate│Hardware│
        │ (REQ) │ (OPT) │ (REQ) │ (REQ) │ (OPT) │ (OPT) │(FUTURE)│
        └───────┴───────┴───────┴───────┴───────┴───────┴───────┘
```

---

## File Structure

```
phase_6/
├── __init__.py           # Module exports
├── config_models.py      # Configuration and result models
├── errors.py             # Deterministic error definitions
├── state_tracker.py      # Queryable execution state
├── pipeline_runner.py    # Main orchestration logic
├── batch_executor.py     # Multi-script batch execution
└── README.md             # Quick reference
```

---

## Core Components

### 1. PipelineConfig

Controls which phases are enabled:

```python
from phase_6 import PipelineConfig

config = PipelineConfig(
    enable_phase_5=True,    # Visualization
    enable_phase_7=False,   # Evaluation
    enable_phase_8=False,   # Hardware (future)
    demo_mode=False,
    use_llm=False           # Pass-through to Phase 4
)
```

### 2. PipelineRunner

Main orchestration class:

```python
from phase_6 import PipelineRunner

runner = PipelineRunner(config)
result = runner.run("data/raw_scripts/Script-1.txt")

print(result.final_status)       # PhaseStatus.SUCCESS
print(result.total_duration_seconds)
```

### 3. BatchExecutor

Multi-script processing:

```python
from phase_6 import BatchExecutor

executor = BatchExecutor(config)

# Process directory
results = executor.run_directory("data/raw_scripts/", pattern="*.txt")

# Process list
results = executor.run_batch([script1, script2, script3])

# Get summary
summary = executor.summarize_results(results)
```

### 4. StateTracker

Query execution state at any time:

```python
state = runner.get_state()
print(f"Current phase: {state.current_phase}")
print(f"Scene: {state.current_scene_id}")
print(f"Progress: {state.current_scene_index}/{state.total_scenes}")
```

---

## Execution Order (LOCKED)

Phase 6 executes phases in this **exact order**:

| Order | Phase | Required | Failure Handling |
|-------|-------|----------|------------------|
| 1 | Phase 1: Parsing | ✅ YES | HARD FAIL |
| 2 | Phase 2: Emotion | ❌ NO | Continue (emotion=null) |
| 3 | Phase 3: RAG | ✅ YES | HARD FAIL |
| 4 | Phase 4: Decision | ✅ YES | HARD FAIL (after fallback) |
| 5 | Phase 5: Simulation | ❌ NO | Log & Continue |
| 6 | Phase 7: Evaluation | ❌ NO | Log & Continue |
| 7 | Phase 8: Hardware | ❌ NO | NOT IMPLEMENTED |

---

## Error Handling

### Error Types

| Error Class | When Used |
|-------------|-----------|
| `HardFailureError` | Required phase fails → stop pipeline |
| `NonFatalError` | Optional phase fails → log and continue |
| `ContractViolationError` | Output violates schema |
| `ConfigurationError` | Invalid config |

### Failure Matrix

```
Phase 1 FAIL  →  STOP (HardFailureError)
Phase 2 FAIL  →  CONTINUE (emotion = null)
Phase 3 FAIL  →  STOP (HardFailureError)
Phase 4 FAIL  →  Allow fallback, then STOP if still fails
Phase 5 FAIL  →  LOG + CONTINUE
Phase 7 FAIL  →  LOG + CONTINUE
```

---

## Result Models

### PhaseResult

```python
@dataclass
class PhaseResult:
    phase_name: str
    status: PhaseStatus      # PENDING/RUNNING/SUCCESS/FAILED/SKIPPED
    output: Optional[dict]
    error_message: Optional[str]
    duration_seconds: float
```

### PipelineResult

```python
@dataclass
class PipelineResult:
    script_path: str
    phase_results: List[PhaseResult]
    total_duration_seconds: float
    final_status: PhaseStatus
    output_paths: dict
```

---

## Contract Enforcement

Phase 6 enforces **ONLY**:

| Check Point | Validation |
|-------------|------------|
| Before Phase 4 | Scene has required fields |
| After Phase 4 | `intensity ∈ [0, 1]`, `group_id` present |

Phase 6 does **NOT** validate:
- Visual correctness
- Artistic quality
- Metrics meaning

---

## Logging

Phase 6 logs:
- Phase start/end times
- Duration per phase
- Failure reasons
- Skip reasons

```
INFO  Phase 1: Starting script parsing
INFO  Phase 1: Parsed 5 scenes
INFO  Phase 4: Starting decision engine
INFO  Pipeline completed: SUCCESS in 2.34s
```

---

## Hard Boundaries

Phase 6 **MUST NOT**:
- ❌ Make lighting decisions
- ❌ Interpret emotions
- ❌ Render visuals
- ❌ Compute metrics
- ❌ Talk to hardware
- ❌ Modify phase outputs
- ❌ Retry silently
- ❌ Swallow errors

Phase 6 **MUST**:
- ✅ Treat phases as black boxes
- ✅ Only call published entry points
- ✅ Log all phase transitions
- ✅ Report failures explicitly

---

## Usage Examples

### Minimal Pipeline

```python
from phase_6 import PipelineRunner

runner = PipelineRunner()
result = runner.run("script.txt")
```

### Skip Visualization

```python
from phase_6 import PipelineRunner, PipelineConfig

config = PipelineConfig(enable_phase_5=False)
runner = PipelineRunner(config)
result = runner.run("script.txt")
```

### Batch Processing

```python
from phase_6 import BatchExecutor, PipelineConfig

config = PipelineConfig(enable_phase_5=False, enable_phase_7=False)
executor = BatchExecutor(config)

results = executor.run_directory("data/raw_scripts/")
summary = executor.summarize_results(results)

print(f"Success: {summary['successful']}/{summary['total_scripts']}")
```

### Check State During Execution

```python
runner = PipelineRunner(config)
# Start in thread, then:
state = runner.get_state()
summary = runner.get_summary()
```

---

## Integration with Other Phases

| Phase | How Phase 6 Interacts |
|-------|----------------------|
| Phase 1 | Calls `segment_scenes()`, `detect_format()` |
| Phase 2 | Calls `analyze_emotion()` |
| Phase 3 | Calls `get_retriever().build_context_for_llm()` |
| Phase 4 | Calls `LightingDecisionEngine.generate_instruction()` |
| Phase 5 | Imports `playback_engine` (optional) |
| Phase 7 | Not yet implemented |
| Phase 8 | Not yet implemented |

---

## Configuration Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enable_phase_5` | bool | `True` | Run visualization |
| `enable_phase_7` | bool | `True` | Run evaluation |
| `enable_phase_8` | bool | `False` | Run hardware (future) |
| `demo_mode` | bool | `False` | Demo execution mode |
| `use_llm` | bool | `False` | Pass to Phase 4 |
| `output_dir` | str | `None` | Output directory |
