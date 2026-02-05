# Phase 4: Lighting Decision Engine

## Overview

Phase 4 is the **Decision Engine** of the Automated Auditorium Lighting system. It converts scene emotions into lighting **INTENT** (not execution details).

**Key principle:** Outputs groups and semantic parameters, never DMX channels or fixture IDs.

---

## Architecture Position

```
Phase 1 → Phase 2 → Phase 3 → [Phase 4] → Phase 5 → Phase 7 → Phase 8
 Parsing   Emotion    RAG      Decision   Simulate  Evaluate  Hardware
```

### Inputs
- **Scene data** (from Phase 1): Structured JSON with content, timing
- **Emotion** (from Phase 2): Primary emotion, confidence
- **RAG context** (from Phase 3): Auditorium knowledge, lighting semantics

### Outputs
- **LightingInstruction**: Group-level, semantic lighting intent

---

## File Structure

```
phase_4/
├── __init__.py                    # Module exports
└── lighting_decision_engine.py    # Core decision engine
```

---

## Core Components

### LightingDecisionEngine

The main class that converts scene data into lighting instructions.

```python
from phase_4 import LightingDecisionEngine, PipelineConfig

engine = LightingDecisionEngine(use_llm=False)
instruction = engine.generate_instruction(scene_data)
```

### Output Models (Pydantic)

| Model | Purpose |
|-------|---------|
| `LightingInstruction` | Complete output from Phase 4 |
| `GroupLightingInstruction` | Per-group lighting settings |
| `LightingParameters` | Semantic parameters (intensity, color, focus) |
| `TimeWindow` | Start/end timing |
| `Transition` | Transition type and duration |

---

## Contract Compliance

Phase 4 output must satisfy `contracts/lighting_instruction_schema.json`:

| Field | Constraint |
|-------|------------|
| `group_id` | String (not fixture_id) |
| `intensity` | Float ∈ [0, 1] |
| `color` | Semantic name (e.g., "warm_amber") |
| `transition.type` | "cut", "fade", or "crossfade" |

---

## Lighting Groups

Phase 4 operates at **group level**, not fixture level:

| Group ID | Description |
|----------|-------------|
| `front_wash` | Primary audience-facing illumination |
| `back_light` | Separation from background, silhouettes |
| `side_fill` | Side lighting for depth and dimension |
| `specials` | Focused highlights, spotlights |
| `ambient` | Overall wash, atmosphere |

---

## Generation Modes

### LLM Mode
- Uses LangChain with OpenAI
- Structured output parsing via Pydantic
- Requires `OPENAI_API_KEY`

### Rule-Based Mode (Fallback)
- Deterministic palette-based generation
- No external API required
- Always produces valid output

```python
# Using LLM
engine = LightingDecisionEngine(use_llm=True)

# Using rules only
engine = LightingDecisionEngine(use_llm=False)
```

---

## Fallback Behavior

1. If LLM unavailable → use rule-based
2. If LLM fails → fallback to rules (if `FALLBACK_TO_RULES=True`)
3. If both fail → raise exception (Phase 6 handles)

---

## Interfaces

### RetrieverProtocol

Phase 4 uses a protocol interface for Phase 3 retriever:

```python
class RetrieverProtocol(Protocol):
    def retrieve_palette(self, emotion: str) -> Dict: ...
    def build_context_for_llm(self, emotion: str, scene_text: str) -> str: ...
```

### SimpleRetriever

Built-in fallback when Phase 3 is unavailable.

---

## Hard Boundaries

Phase 4 **MUST NOT**:
- ❌ Output DMX channels
- ❌ Output fixture IDs
- ❌ Import from Phase 5, 7, or 8
- ❌ Render visuals
- ❌ Execute hardware commands

Phase 4 **MUST**:
- ✅ Output `group_id` only
- ✅ Use normalized intensity [0, 1]
- ✅ Use semantic color names
- ✅ Provide declarative transitions

---

## Usage Examples

### Single Scene

```python
from phase_4 import generate_lighting_instruction

scene_data = {
    "scene_id": "scene_001",
    "emotion": {"primary_emotion": "joy"},
    "content": {"text": "A celebration begins!"},
    "timing": {"start_time": 0, "end_time": 30}
}

instruction = generate_lighting_instruction(scene_data, use_llm=False)
print(instruction.groups[0].parameters.intensity)  # 0.8
```

### Batch Processing

```python
from phase_4 import batch_generate_instructions

scenes = [scene1, scene2, scene3]
instructions = batch_generate_instructions(scenes, use_llm=False)
```

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `LLM_MODEL` | str | "gpt-4" | OpenAI model |
| `LLM_TEMPERATURE` | float | 0.7 | Generation temperature |
| `FALLBACK_TO_RULES` | bool | True | Use rules on LLM failure |

---

## Testing

Tests are located in `tests/test_cue_generator.py`:

- Model validation tests
- Rule-based generation tests
- No DMX leakage verification
- Group-level output verification

```bash
pytest tests/test_cue_generator.py -v
```
