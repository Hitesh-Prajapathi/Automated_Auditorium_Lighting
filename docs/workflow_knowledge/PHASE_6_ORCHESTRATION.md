# PHASE 6: ORCHESTRATION

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 6 is the **orchestration spine** of the system. It controls the execution order, manages state, and handles failures. It does NOT contain any domain logic.

### What Problem It Solves
With 7+ phases, someone needs to:
- Call phases in the right order
- Pass data between phases correctly
- Handle failures gracefully
- Track execution state

Phase 6 does this without influencing lighting decisions.

### What Question It Answers
> "How do phases get called, and in what order?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_6/`

```
phase_6/
├── __init__.py           # Module exports
├── README.md             # Phase documentation
├── pipeline_runner.py    # Main orchestration logic
├── batch_executor.py     # Multi-script processing
├── config_models.py      # Configuration and result models
├── errors.py             # Custom error types
└── state_tracker.py      # Execution state tracking
```

---

### File: `phase_6/__init__.py`

**Exports:**
- `PipelineRunner`
- `BatchExecutor`
- `PipelineConfig`
- `PipelineResult`, `PhaseResult`
- Error types

---

### File: `phase_6/pipeline_runner.py`

**Why This File Exists:**
Contains the main `PipelineRunner` class that orchestrates execution.

**Size:** ~424 lines

---

### File: `phase_6/batch_executor.py`

**Why This File Exists:**
Processes multiple scripts (batch mode).

**Key Class:** `BatchExecutor`
- `run_batch(scripts)`: Process list of scripts
- `run_directory(path)`: Process all scripts in folder

---

### File: `phase_6/config_models.py`

**Why This File Exists:**
Defines configuration and result structures.

**Key Classes:**
- `PipelineConfig`: Enable/disable phases
- `PhaseResult`: Single phase outcome
- `PipelineResult`: Complete run outcome

---

### File: `phase_6/errors.py`

**Why This File Exists:**
Custom error types for failure handling.

**Error Types:**
- `HardFailureError`: Fatal, stops pipeline
- `NonFatalError`: Warning, continues
- `ContractViolationError`: Schema mismatch
- `PhaseNotImplementedError`: Phase called but not ready

---

### File: `phase_6/state_tracker.py`

**Why This File Exists:**
Tracks execution state for observability.

**Key Class:** `StateTracker`
- Tracks current phase, scene, status
- Provides queryable snapshot

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

### Class: `PipelineRunner`

**Purpose:**
Main orchestrator. Executes phases in order.

**Constructor:**
```python
def __init__(self, config: PipelineConfig = None):
```

**Internal State:**
- `self.config`: Pipeline configuration
- `self.state_tracker`: StateTracker instance
- `self.results`: List of PhaseResult

**Lifecycle:**
1. Instantiated with config
2. `run(script_path)` or `run_text(text)` called
3. Phases executed in order
4. Returns PipelineResult

---

### Class: `PipelineConfig`

**Purpose:**
Controls which phases to enable.

**Fields:**
```python
enable_phase_1: bool = True
enable_phase_2: bool = True   # Optional
enable_phase_3: bool = True
enable_phase_4: bool = True
enable_phase_5: bool = True
enable_phase_7: bool = True   # Metrics
enable_phase_8: bool = False  # Hardware (disabled by default)
use_llm: bool = True
```

---

### Class: `PhaseResult`

**Purpose:**
Outcome of a single phase execution.

**Fields:**
```python
phase: int
success: bool
data: Any
error: Optional[str]
duration: float
```

---

### Class: `PipelineResult`

**Purpose:**
Complete run outcome.

**Fields:**
```python
success: bool
phases: List[PhaseResult]
final_output: Any
total_duration: float
```

---

### Class: `StateTracker`

**Purpose:**
Observable execution state.

**Key Methods:**
- `set_phase(phase_num)`: Update current phase
- `set_scene(scene_id)`: Update current scene
- `set_status(status)`: Update status string
- `get_snapshot()`: Return current state dict

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `PipelineRunner.run(script_path: str) -> PipelineResult`

**Exact Responsibility:**
Execute full pipeline on a script file.

**Implementation:**
1. Read script file
2. Call `run_text(text)`
3. Return result

---

### `PipelineRunner.run_text(text: str) -> PipelineResult`

**Exact Responsibility:**
Execute full pipeline on raw text.

**Implementation:**
```
1. Phase 1: Parse script → scenes
2. For each scene:
   a. Phase 2: Enrich with emotion (if enabled)
   b. Phase 3: Get RAG context (implicit in Phase 4)
   c. Phase 4: Generate LightingInstruction
   d. Phase 5: Queue for visualization (if enabled)
3. Phase 7: Compute metrics (if enabled)
4. Return PipelineResult
```

---

### `PipelineRunner._run_phase_1(text: str) -> List[dict]`

**Exact Responsibility:**
Call Phase 1 and return scene list.

**Failure Handling:**
Raises `HardFailureError` on failure (Phase 1 is required).

---

### `PipelineRunner._run_phase_2(scene: dict) -> dict`

**Exact Responsibility:**
Enrich scene with emotion.

**Failure Handling:**
- NonFatalError → returns scene unchanged
- Scene continues with emotion=None

---

### `PipelineRunner._run_phase_4(scene: dict) -> LightingInstruction`

**Exact Responsibility:**
Generate lighting intent for scene.

**Contract Validation:**
- Validates output intensity in [0, 1]
- Validates group_id presence
- Raises `ContractViolationError` on failure

---

### `PipelineRunner._validate_lighting_instruction(instruction)`

**Exact Responsibility:**
Enforce Phase 4 output contract.

**Checks:**
- `group_id` in each group
- `intensity` in [0, 1]

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 6 ORCHESTRATION FLOW                                     │
│ Canonical Order: 1 → 2 → 3 → 4 → 5 → 7                          │
└─────────────────────────────────────────────────────────────────┘

1. PipelineRunner.run(script_path)
          │
          ▼
2. _run_phase_1(text)
   └── Returns List[Scene]
          │
          ▼
3. FOR EACH scene:
   ├── _run_phase_2(scene) [if enabled]
   │   └── Enriches scene.emotion
   │
   ├── _run_phase_4(scene)
   │   ├── Calls LightingDecisionEngine
   │   ├── _validate_lighting_instruction()
   │   └── Returns LightingInstruction
   │
   └── _run_phase_5(instruction) [if enabled]
       └── Queues for visualization
          │
          ▼
4. _run_phase_7(instructions) [if enabled]
   └── Computes metrics
          │
          ▼
5. Return PipelineResult
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### PipelineResult
```python
{
    "success": bool,
    "phases": [
        {
            "phase": int,
            "success": bool,
            "data": Any,
            "error": str | None,
            "duration": float
        }
    ],
    "final_output": List[LightingInstruction],
    "total_duration": float
}
```

---

## 7️⃣ FAILURE BEHAVIOR

### Phase 1 Fails
- `HardFailureError` raised
- Pipeline stops immediately
- Returns failed PipelineResult

### Phase 2 Fails
- `NonFatalError` logged
- Scene continues without emotion
- **Pipeline continues**

### Phase 4 Fails
- `HardFailureError` raised
- That scene fails
- Pipeline may continue to next scene (configurable)

### Contract Violation
- `ContractViolationError` raised
- Converted to `HardFailureError`
- Scene fails

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 6 MUST NOT Do:
- ❌ Must NOT parse scripts (that's Phase 1)
- ❌ Must NOT analyze emotions (that's Phase 2)
- ❌ Must NOT query RAG (that's Phase 3)
- ❌ Must NOT generate lighting (that's Phase 4)
- ❌ Must NOT visualize (that's Phase 5)
- ❌ Must NOT evaluate (that's Phase 7)
- ❌ Must NOT send hardware commands (that's Phase 8)

### What Phase 6 MUST Do:
- ✅ Call phases in correct order
- ✅ Pass data between phases correctly
- ✅ Handle errors deterministically
- ✅ Track execution state

### Principle: ORCHESTRATION ONLY
Phase 6 is a dumb router. It doesn't know what lighting is.
It just knows to call Phase N and pass the result to Phase N+1.

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why is Phase 3 not explicitly called?"

Phase 3 (RAG) is called internally by Phase 4.
Phase 6 doesn't need to orchestrate it directly.

### "Why does Phase 6 validate Phase 4 output?"

Contract enforcement must happen SOMEWHERE.
Phase 6 is the natural point because it sits between phases.
Phase 4 should also validate, but Phase 6 acts as a safety net.

### "Why is Phase 8 disabled by default?"

Phase 8 controls real hardware. Enabling it accidentally could:
- Damage equipment
- Cause safety hazards
- Interfere with live shows

Explicit opt-in is required.

### "Why does Phase 6 treat phases as black boxes?"

This is intentional. Phase 6 only knows:
- Phase N exists
- Phase N has an entry point
- Phase N returns something

It doesn't know WHAT Phase N does. This enables:
- Independent development
- Easy testing
- Clean architecture

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 6:
1. **Deterministic order**: Phases always called in same order
2. **Error isolation**: One phase failure doesn't crash others
3. **Contract enforcement**: Invalid outputs are caught
4. **State observability**: Execution state is queryable

### Invariants Maintained:
- Phase order is always 1 → 2 → 3 → 4 → 5 → 7 → 8
- Every phase gets valid input (per contract)
- Every result is logged

### What Would Break If Phase 6 Were Removed:
- No way to run the full pipeline
- Manual phase invocation required
- No centralized error handling
- No execution tracking
