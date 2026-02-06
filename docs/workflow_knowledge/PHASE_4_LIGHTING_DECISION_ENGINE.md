# PHASE 4: LIGHTING DECISION ENGINE

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 4 is the **AI brain** of the system. It takes scene data (from Phase 1, enriched by Phase 2, with context from Phase 3) and generates **semantic lighting intent**.

### What Problem It Solves
Converting "a sad scene in a drama" into "use front wash at 30% intensity with cool blue color and slow fade" requires:
- Understanding theatrical lighting design
- Mapping emotions to visual parameters
- Selecting appropriate fixture groups

Phase 4 uses an LLM (or rule-based fallback) to make these decisions.

### What Question It Answers
> "What lighting SHOULD this scene have?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_4/`

Contains 2 files.

---

### File: `phase_4/__init__.py`

**Why This File Exists:**
Exports the public API.

**Exports:**
- `LightingDecisionEngine` — main class
- Output models (Pydantic)

**Who Calls It:**
- Phase 6 `_run_phase_4()`

---

### File: `phase_4/lighting_decision_engine.py`

**Why This File Exists:**
Contains all lighting decision logic including:
- LLM-based intent generation
- Rule-based fallback
- Pydantic output models

**Dependencies:**
- `langchain_openai.ChatOpenAI`
- `pydantic`

**Size:** ~470 lines

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

### Class: `LightingParameters` (Pydantic)

**Purpose:**
Defines the parameter structure for a fixture group.

**Fields:**
- `intensity` (float): 0.0-1.0 normalized
- `color` (Optional[str]): Semantic color name
- `focus_area` (Optional[str]): Abstract stage area

---

### Class: `LightingTransition` (Pydantic)

**Purpose:**
Defines transition between lighting states.

**Fields:**
- `type` (Literal["cut", "fade", "crossfade"])
- `duration` (float): Seconds

---

### Class: `GroupInstruction` (Pydantic)

**Purpose:**
Lighting instruction for a single fixture group.

**Fields:**
- `group_id` (str): Logical group identifier
- `parameters` (LightingParameters)
- `transition` (Optional[LightingTransition])

---

### Class: `LightingInstruction` (Pydantic)

**Purpose:**
Complete lighting instruction for a scene. **This is the Phase 4 output contract.**

**Fields:**
- `scene_id` (str)
- `time_window` (dict): {"start": float, "end": float}
- `groups` (List[GroupInstruction])
- `metadata` (Optional[dict]): Debug info

---

### Class: `LightingDecisionEngine`

**Purpose:**
Main engine that generates lighting intent.

**Constructor:**
```python
def __init__(self, use_llm: bool = True):
```
- If `use_llm=True`: Initializes ChatOpenAI with structured output
- Sets up LangChain prompt templates
- Loads fallback rules

**Internal State:**
- `self.use_llm` (bool)
- `self.llm`: ChatOpenAI instance (or None)
- `self.structured_llm`: LLM with Pydantic output parsing
- `self.prompt`: ChatPromptTemplate

**Lifecycle:**
1. Instantiated by Phase 6
2. Called once per scene
3. Stateless between calls

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `LightingDecisionEngine.__init__(use_llm: bool = True)`

**Exact Responsibility:**
Initialize the engine with LLM or fallback mode.

**Side Effects:**
- OpenAI API key validation (if LLM mode)
- Prints initialization status

---

### `LightingDecisionEngine.generate_instruction(scene: dict) -> LightingInstruction`

**Exact Responsibility:**
Main entry point. Generates lighting intent for a scene.

**Input Parameters:**
- `scene` (dict): Scene data matching `scene_schema.json`

**Output Values:**
`LightingInstruction` Pydantic model

**Execution Flow:**
1. Extract scene metadata (emotion, script_type, text)
2. If LLM enabled: call `_generate_with_llm()`
3. Else: call `_generate_with_rules()`
4. Validate output
5. Return instruction

**Failure Modes:**
- LLM call fails → falls back to rules
- Validation fails → raises exception (caught by Phase 6)

---

### `LightingDecisionEngine._generate_with_llm(scene: dict) -> LightingInstruction`

**Exact Responsibility:**
Generate intent using OpenAI GPT.

**Implementation:**
1. Build prompt with scene context
2. Invoke structured LLM
3. Parse response into Pydantic model

**Failure Modes:**
- API key invalid → exception
- Rate limit → exception
- Malformed response → exception

---

### `LightingDecisionEngine._generate_with_rules(scene: dict) -> LightingInstruction`

**Exact Responsibility:**
Rule-based fallback when LLM unavailable.

**Implementation:**
1. Extract emotion from scene
2. Map emotion to predefined lighting rules
3. Build instruction from rules

**Emotion Mappings (hardcoded):**
- `joy` → 0.8 intensity, warm_amber, fade
- `sadness` → 0.3 intensity, cool_blue, slow fade
- `fear` → 0.2 intensity, dark_blue, slow fade
- `anger` → 0.7 intensity, red, fast cut
- `neutral` → 0.6 intensity, natural_white, fade

**Output:**
Always produces valid `LightingInstruction`

---

### `LightingDecisionEngine._build_groups(emotion_rules: dict) -> List[GroupInstruction]`

**Exact Responsibility:**
Convert emotion rules into group instructions.

**Returns:**
List with two default groups:
- `front_wash`
- `ambient_fill`

---

### `LightingDecisionEngine._get_default_groups() -> List[str]`

**Exact Responsibility:**
Return list of default group IDs.

**Returns:**
`["front_wash", "side_light", "back_light", "ambient_fill"]`

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 4 EXECUTION FLOW                                         │
└─────────────────────────────────────────────────────────────────┘

1. INPUT: Scene dict from Phase 1 (enriched with Phase 2 emotion)
          │
          ▼
2. LightingDecisionEngine.generate_instruction(scene)
          │
          ├── LLM enabled?
          │   ├── YES → _generate_with_llm(scene)
          │   │         ├── Build prompt with scene data
          │   │         ├── Invoke ChatOpenAI
          │   │         └── Parse structured response
          │   │
          │   └── NO → _generate_with_rules(scene)
          │             ├── Extract emotion
          │             ├── Map to lighting rules
          │             └── Build instruction
          │
          ▼
3. Validate output (Pydantic)
   ├── intensity in [0, 1]
   ├── group_id present
   └── time_window valid
          │
          ▼
4. OUTPUT: LightingInstruction (contract-compliant)
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Input: Scene (from Phase 1)
```python
{
    "scene_id": str,
    "text": str,
    "time_window": {"start": float, "end": float},
    "script_type": str,
    "emotion": {
        "primary_emotion": str,
        "primary_score": float
    }  # or None
}
```

### Output: LightingInstruction
```python
{
    "scene_id": str,
    "time_window": {"start": float, "end": float},
    "groups": [
        {
            "group_id": str,          # e.g., "front_wash"
            "parameters": {
                "intensity": float,    # 0.0 - 1.0
                "color": str,          # e.g., "warm_amber"
                "focus_area": str      # e.g., "CENTER_STAGE"
            },
            "transition": {
                "type": str,           # "cut", "fade", "crossfade"
                "duration": float      # seconds
            }
        }
    ],
    "metadata": dict | None
}
```

---

## 7️⃣ FAILURE BEHAVIOR

### LLM API Error
- Caught in `_generate_with_llm()`
- Falls back to `_generate_with_rules()`
- **Pipeline continues**

### Invalid Output Structure
- Pydantic validation fails
- Exception raised
- Phase 6 catches as `HardFailureError`
- **Pipeline halts for this scene**

### Missing Emotion Data
- `scene.get("emotion")` returns None
- Falls back to "neutral" emotion
- **Pipeline continues**

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 4 MUST NOT Do:
- ❌ Must NOT output DMX channels (that's Phase 8)
- ❌ Must NOT output fixture-level commands (groups only)
- ❌ Must NOT query RAG directly (Phase 3 provides context)
- ❌ Must NOT render or visualize (that's Phase 5)
- ❌ Must NOT persist data

### What Phase 4 MUST Do:
- ✅ Produce group-level semantic instructions
- ✅ Use normalized intensity [0, 1]
- ✅ Use semantic color names (not hex/RGB)
- ✅ Match `lighting_instruction_schema.json`

### How Phase Isolation Is Enforced:
- No imports from Phase 5, 6, 7, 8
- Output models mirror Phase 0 contracts
- Intensity clamped to [0, 1] in Pydantic validators

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why does Phase 4 use LangChain when it could just call OpenAI directly?"

LangChain provides:
- Structured output parsing (Pydantic integration)
- Prompt templating
- Easier testing/mocking

### "Why is the fallback rule-based instead of just returning an error?"

Production systems need guaranteed output. Rule-based fallback ensures:
- Every scene gets lighting (no gaps)
- System works without API access
- Demos work offline

### "Why are intensity values normalized to [0, 1] instead of 0-255?"

Semantic separation. Intensity is an **intent** (0-1 makes sense abstractly).
0-255 is a **hardware concern** (DMX implementation detail for Phase 8).

### "Why does Phase 4 output group_id instead of fixture_id?"

The lighting decision is about **concepts** (front wash, back light).
Mapping to specific fixtures is Phase 8's job based on venue configuration.

### "Why is 'reasoning' not in the output?"

Earlier versions had a `reasoning` field. It was removed because:
- It's non-executable (just logging)
- It bloated the output
- It leaked LLM internal state

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 4:
1. **Always outputs**: LLM failure → rule-based fallback
2. **Contract compliance**: Pydantic ensures schema adherence
3. **Intensity bounds**: Always [0, 1]
4. **Group-level only**: No fixture IDs in output

### Invariants Maintained:
- Every scene gets a `LightingInstruction`
- `groups` array is never empty
- `scene_id` in output matches input
- `time_window` in output matches input

### What Would Break If Phase 4 Were Removed:
- No lighting decisions for scenes
- Phase 5 would have nothing to visualize
- Phase 6 pipeline would halt at Phase 4
- System would produce no usable output
