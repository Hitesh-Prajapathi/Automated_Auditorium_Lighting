# PHASE 0: CONTRACTS

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 0 defines the **immutable data contracts** that govern all inter-phase communication in the system. These contracts are JSON Schema definitions that specify the exact structure, types, and constraints of data passed between phases.

### What Problem It Solves
Without contracts, phases would have implicit dependencies on each other's implementation details. Any change in one phase could silently break another. Phase 0 solves this by:
- Establishing a single source of truth for data formats
- Enabling independent development of phases
- Providing compile-time-like guarantees for data structure
- Making integration failures visible and debuggable

### What Question It Answers
> "What EXACTLY does the data look like when it crosses phase boundaries?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `contracts/`

This directory contains exactly 4 JSON Schema files. These files are **read-only at runtime** and **never modified by any phase**.

---

### File: `contracts/scene_schema.json`

**Why This File Exists:**
Defines the canonical representation of a "Scene" — the fundamental unit of theatrical content that flows through the pipeline.

**How It Is Used:**
- Phase 1 PRODUCES Scene JSON conforming to this schema
- Phase 2 ENRICHES the `emotion` field (optional)
- Phase 3 READS the `text` field for RAG queries
- Phase 4 READS scene data to generate lighting intent
- Phase 6 ENFORCES this structure during orchestration

**When It Is Imported:**
This file is NOT imported as Python code. It is referenced for:
1. Manual validation during development
2. Documentation of expected structure
3. Test assertions

**Who Calls It:**
No runtime caller. It is a specification document.

---

### File: `contracts/lighting_instruction_schema.json`

**Why This File Exists:**
Defines the `LightingInstruction` — the output of Phase 4 that represents **lighting intent** (not hardware commands).

**How It Is Used:**
- Phase 4 PRODUCES `LightingInstruction` objects conforming to this schema
- Phase 5 CONSUMES instructions for visualization
- Phase 6 VALIDATES instructions during pipeline execution
- Phase 7 EVALUATES instructions for metrics
- Phase 8 CONSUMES instructions for hardware translation (future)

**When It Is Imported:**
Not imported. Referenced for validation logic in Phase 4's Pydantic models and Phase 6's contract enforcement.

**Who Calls It:**
Referenced by `phase_4/lighting_decision_engine.py` (Pydantic models mirror this schema).

---

### File: `contracts/fixture_schema.json`

**Why This File Exists:**
Defines the metadata structure for a **physical lighting fixture** in the auditorium. This is NOT used for hardware control — it describes fixture capabilities semantically.

**How It Is Used:**
- Phase 3 uses this structure in the Auditorium RAG knowledge base
- Phase 8 (future) would use fixture metadata for DMX mapping

**When It Is Imported:**
Not imported. The structure is embedded in `phase_3/knowledge/auditorium/fixtures.json`.

**Who Calls It:**
Phase 3 RAG retriever returns fixture metadata in this format.

---

### File: `contracts/lighting_semantics_schema.json`

**Why This File Exists:**
Defines **design rules** for lighting — how emotions, script types, and scene functions map to lighting tendencies (color palettes, intensity ranges, transitions).

**How It Is Used:**
- Phase 3 stores lighting semantics in RAG knowledge base
- Phase 4 queries Phase 3 for semantics when generating lighting intent
- Rule-based fallback in Phase 4 uses hardcoded versions of this structure

**When It Is Imported:**
Not imported. The structure guides Phase 3's knowledge ingestion and Phase 4's retriever protocol.

**Who Calls It:**
Phase 3's `rag_retriever.py` returns data in this format.

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

Phase 0 contains **no classes**. It is pure JSON Schema.

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

Phase 0 contains **no functions**. It is pure JSON Schema.

---

## 5️⃣ EXECUTION FLOW

Phase 0 has **no execution flow**. These are static schema definitions.

```
Phase 0 is NOT executed.
Phase 0 is CONSULTED at development time.
Phase 0 is MIRRORED by runtime Pydantic models.
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Scene Schema (`scene_schema.json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scene_id` | string | ✅ | Unique identifier for the scene |
| `script_type` | enum | ✅ | One of: `timestamped_drama`, `raw_drama`, `event_schedule`, `cue_sheet`, `mixed` |
| `time_window` | object | ✅ | Contains `start` and `end` (numbers, seconds) |
| `text` | string | ✅ | Raw scene text for downstream analysis |
| `location` | string/null | ❌ | Optional stage area identifier |
| `emotion` | object/null | ❌ | Phase 2 enrichment (primary, secondary, confidence) |
| `explicit_lighting` | array[string] | ❌ | Verbatim lighting cues from script |

**Who Populates:**
- `scene_id`, `script_type`, `time_window`, `text`, `location`, `explicit_lighting`: Phase 1
- `emotion`: Phase 2 (optional)

**Who Consumes:**
- Phase 3 (for RAG queries)
- Phase 4 (for lighting decision generation)
- Phase 6 (for orchestration)

---

### LightingInstruction Schema (`lighting_instruction_schema.json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `scene_id` | string | ✅ | Links back to source scene |
| `time_window` | object | ✅ | When this instruction applies |
| `groups` | array | ✅ | List of group instructions |
| `metadata` | object/null | ❌ | Debug info, reasoning (non-executable) |

**Group Structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `group_id` | string | ✅ | Logical fixture group (e.g., `front_wash`) |
| `parameters.intensity` | number [0,1] | ✅ | Normalized intensity |
| `parameters.color` | string | ❌ | Semantic color name |
| `parameters.focus_area` | string/null | ❌ | Abstract focus region |
| `transition.type` | enum | ❌ | `cut`, `fade`, or `crossfade` |
| `transition.duration` | number | ❌ | Transition duration in seconds |

**Who Populates:**
- Phase 4 (LightingDecisionEngine)

**Who Consumes:**
- Phase 5 (visualization)
- Phase 6 (validation)
- Phase 7 (evaluation)
- Phase 8 (hardware translation, future)

---

### Fixture Schema (`fixture_schema.json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fixture_id` | string | ✅ | Unique fixture identifier |
| `group_id` | string | ✅ | Logical group membership |
| `fixture_type` | enum | ✅ | `par`, `wash`, `spot`, `beam`, `fresnel` |
| `position` | object | ✅ | 3D coordinates (x, y, z) |
| `capabilities` | array | ✅ | `dim`, `rgb`, `cmy`, `pan`, `tilt`, `zoom` |
| `constraints` | object | ❌ | Physical/safety constraints |

**Who Populates:**
- Manual configuration in `phase_3/knowledge/auditorium/fixtures.json`

**Who Consumes:**
- Phase 3 RAG (returns fixture metadata)
- Phase 8 (future, for DMX mapping)

---

### LightingSemantics Schema (`lighting_semantics_schema.json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `context_type` | enum | ✅ | `emotion`, `script_type`, `scene_function`, `event_phase` |
| `context_value` | string | ✅ | The specific value (e.g., "joy", "drama") |
| `rules.intensity.preferred_range` | [number, number] | ❌ | Intensity bounds |
| `rules.color.palette` | array[string] | ❌ | Suggested color names |
| `rules.color.temperature` | enum | ❌ | `warm`, `neutral`, `cool` |
| `rules.transition.preferred_types` | array[enum] | ❌ | Preferred transition types |
| `priority` | number [0,1] | ❌ | Override priority |

**Who Populates:**
- Manual configuration in `phase_3/knowledge/semantics/baseline_semantics.json`

**Who Consumes:**
- Phase 3 RAG (returns semantic rules)
- Phase 4 (uses rules for lighting generation)

---

## 7️⃣ FAILURE BEHAVIOR

Phase 0 **cannot fail** — it is static data.

If a phase produces data that violates a contract:
- The violation is **not caught at Phase 0** (contracts are not automatically enforced)
- The violation is caught by:
  - Phase 4's Pydantic models (for LightingInstruction)
  - Phase 6's manual validation (for contract enforcement during orchestration)

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 0 MUST NOT Do:
- Phase 0 must NOT contain logic
- Phase 0 must NOT be imported as Python modules
- Phase 0 must NOT be modified by any runtime process

### What Other Phases MUST NOT Do:
- No phase may modify contracts at runtime
- No phase may loosen contract requirements
- No phase may add fields outside the defined schema (due to `additionalProperties: false`)

### How Phase Isolation Is Enforced:
- Contracts are JSON files (not Python, so no accidental execution)
- `additionalProperties: false` prevents undocumented field creep
- Runtime models (Pydantic) mirror these schemas exactly

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why are contracts in JSON and not Pydantic?"

The contracts are **specification documents** intended to be:
- Language-agnostic (could be consumed by non-Python systems)
- Human-readable without Python knowledge
- Stable anchors that don't change when implementation changes

Pydantic models in Phase 4 are **implementations** of these contracts.

### "Why is `emotion` nullable in the scene schema?"

Phase 2 (Emotion Enrichment) is **optional**. If Phase 2 is disabled or fails, `emotion` will be `null`. Downstream phases must handle this gracefully.

### "Why does the fixture schema have `group_id` when it also has `fixture_id`?"

- `fixture_id` identifies a single physical fixture (e.g., "PAR_001")
- `group_id` identifies the logical group it belongs to (e.g., "front_wash")

The lighting decision system operates on **groups**, not fixtures. Phase 8 (future) translates group-level intent to fixture-level commands.

### "Why is `additionalProperties: false` on all schemas?"

This prevents "schema drift" where new fields are added without updating the contract. Every field must be explicitly defined.

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 0:
1. **Structure guarantee**: Data crossing phase boundaries has a defined shape
2. **Type guarantee**: Field types are constrained (numbers, strings, enums)
3. **Constraint guarantee**: Value ranges are enforced (e.g., intensity 0-1)
4. **Completeness guarantee**: Required fields must be present

### Invariants Maintained:
- Contracts NEVER change at runtime
- All inter-phase data is representable in JSON
- No phase may bypass contracts

### What Would Break If Phase 0 Were Removed:
- Phases would have implicit dependencies on each other's internals
- Changes in one phase would silently break others
- Integration failures would be cryptic and hard to debug
- No single source of truth for data formats
