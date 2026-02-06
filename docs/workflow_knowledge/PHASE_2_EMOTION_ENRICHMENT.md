# PHASE 2: EMOTION ENRICHMENT

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 2 **optionally enriches** Scene data with emotion analysis. It extracts emotional signals from scene text to inform lighting decisions downstream.

### What Problem It Solves
Lighting often reflects mood. Without emotion analysis, Phase 4 would have no semantic signal about whether a scene is joyful, tense, or melancholic. Phase 2 provides this semantic context.

### What Question It Answers
> "What is the emotional tone of this scene?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_2/`

Contains 2 files.

---

### File: `phase_2/__init__.py`

**Why This File Exists:**
Exports the public API of Phase 2.

**How It Is Used:**
Imported by Phase 6 orchestrator.

**When It Is Imported:**
```python
from phase_2 import analyze_emotion
```

**Who Calls It:**
- `phase_6/pipeline_runner.py`
- `main.py`

**Exports:**
- `analyze_emotion` — convenience function

---

### File: `phase_2/emotion_analyzer.py`

**Why This File Exists:**
Contains all emotion analysis logic with ML model and keyword fallback.

**How It Is Used:**
Analyzes scene text to produce emotion metadata.

**When It Is Imported:**
By `__init__.py`.

**Who Calls It:**
Via `analyze_emotion()` from Phase 6 or main.

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

### Class: `EmotionAnalyzer`

**Purpose:**
Dual-mode emotion analyzer supporting ML (DistilRoBERTa) and keyword fallback.

**Constructor Behavior:**
```python
def __init__(self, use_ml=USE_ML_EMOTION):
```
- Checks if ML dependencies are available (`transformers`, `torch`)
- If available and `use_ml=True`, initializes HuggingFace pipeline
- Loads keyword dictionary for fallback
- Sets `self.ml_available` flag

**Internal State:**
- `self.ml_available` (bool): Whether ML model is ready
- `self.classifier`: HuggingFace pipeline (or None)
- `self.keywords` (dict): Keyword-to-emotion mapping

**Lifecycle:**
1. Created once (singleton pattern via `get_analyzer()`)
2. Persists for all scene analyses
3. No cleanup required

**Who Instantiates It:**
- `get_analyzer()` creates singleton
- `analyze_emotion()` uses singleton

**Who Consumes It:**
- Phase 6 via `analyze_emotion()` function

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `EmotionAnalyzer.analyze(text: str) -> dict`

**Exact Responsibility:**
Main analysis entry point. Routes to ML or keyword analysis.

**Input Parameters:**
- `text` (str): Scene text to analyze

**Output Values:**
```python
{
    "primary_emotion": str,      # Dominant emotion
    "primary_score": float,      # Confidence 0-1
    "secondary_emotion": str|None,
    "secondary_score": float,
    "all_scores": dict,          # All emotion scores
    "method": str                # "ml", "keyword", or "default"
}
```

**Side Effects:** None

**Failure Modes:**
- Empty text → returns neutral response
- ML failure → falls back to keyword analysis
- **Never fails** (always returns valid structure)

---

### `EmotionAnalyzer._ml_analyze(text: str) -> dict`

**Exact Responsibility:**
ML-based analysis using DistilRoBERTa emotion classifier.

**Input Parameters:**
- `text` (str): Text to analyze (truncated to 2000 chars)

**Output Values:**
Same structure as `analyze()` with `"method": "ml"`

**Side Effects:** 
- GPU usage if CUDA available

**Failure Modes:**
- Model error → falls back to `_keyword_analyze()`
- Token overflow → handled by truncation

---

### `EmotionAnalyzer._keyword_analyze(text: str) -> dict`

**Exact Responsibility:**
Fallback keyword matching analysis.

**Input Parameters:**
- `text` (str): Text to analyze

**Output Values:**
Same structure as `analyze()` with `"method": "keyword"`

**Failure Modes:**
- No keywords found → returns neutral response

---

### `EmotionAnalyzer._neutral_response() -> dict`

**Exact Responsibility:**
Returns default neutral emotion structure.

**Output Values:**
```python
{
    "primary_emotion": "neutral",
    "primary_score": 1.0,
    "secondary_emotion": None,
    "secondary_score": 0,
    "all_scores": {"neutral": 1.0},
    "method": "default"
}
```

---

### `EmotionAnalyzer._load_keywords() -> dict`

**Exact Responsibility:**
Returns hardcoded keyword dictionary for 7 emotions.

**Emotions Covered:**
- joy, sadness, anger, fear, surprise, disgust, neutral

---

### `get_analyzer() -> EmotionAnalyzer`

**Exact Responsibility:**
Singleton factory. Creates analyzer on first call, returns existing on subsequent.

**Output Values:**
`EmotionAnalyzer` instance

---

### `analyze_emotion(text: str) -> dict`

**Exact Responsibility:**
Public convenience function for emotion analysis.

**This is the published API.** All external calls should use this.

**Input Parameters:**
- `text` (str): Text to analyze

**Output Values:**
Same structure as `EmotionAnalyzer.analyze()`

**Where Called From:**
- Phase 6 `_run_phase_2()`
- `main.py`

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2 EXECUTION FLOW                                         │
└─────────────────────────────────────────────────────────────────┘

1. INPUT: Scene text from Phase 1
          │
          ▼
2. analyze_emotion(text)
   └── get_analyzer() → singleton EmotionAnalyzer
          │
          ▼
3. EmotionAnalyzer.analyze(text)
   ├── Empty text? → _neutral_response()
   ├── ML available? → _ml_analyze(text)
   └── Otherwise → _keyword_analyze(text)
          │
          ▼
4. OUTPUT: Emotion dict with primary/secondary emotions
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Input: Scene Text
- Plain string
- May be empty
- May contain any content type

### Output: Emotion Analysis
```python
{
    "primary_emotion": str,      # e.g., "joy", "sadness", "neutral"
    "primary_score": float,      # 0.0 - 1.0
    "secondary_emotion": str|None,
    "secondary_score": float,    # 0.0 - 1.0
    "all_scores": {
        "joy": float,
        "sadness": float,
        # ... etc
    },
    "method": str               # "ml", "keyword", "default"
}
```

### Keyword Dictionary Structure
```python
{
    "joy": ["happy", "smile", "love", ...],
    "sadness": ["sad", "cry", "lonely", ...],
    # ... 7 emotions total
}
```

---

## 7️⃣ FAILURE BEHAVIOR

### ML Dependency Missing
- `ML_AVAILABLE = False`
- Warning printed at import time
- All calls use keyword fallback
- **Execution continues**

### ML Model Load Fails
- Warning printed
- Falls back to keyword analysis
- **Execution continues**

### ML Analysis Fails Mid-Execution
- Warning printed
- Falls back to keyword analysis for that call
- **Execution continues**

### Empty/Invalid Text
- Returns neutral response
- **Execution continues**

**Phase 2 is designed to NEVER fail the pipeline.**

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 2 MUST NOT Do:
- ❌ Must NOT parse scripts (that's Phase 1)
- ❌ Must NOT query RAG (that's Phase 3)
- ❌ Must NOT generate lighting (that's Phase 4)
- ❌ Must NOT influence execution (it's observational)

### What Phase 2 MUST Do:
- ✅ Accept text, return emotion dict
- ✅ Handle missing ML dependencies gracefully
- ✅ Never block pipeline on failure

### How Phase Isolation Is Enforced:
- Only imports from `config.py` and `transformers`
- No imports from other phases
- Output is pure data (no side effects on scene)

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why is there both a class and a function?"

The `EmotionAnalyzer` class manages state (singleton, loaded model).
The `analyze_emotion()` function is the clean public API that hides that complexity.

External code should ONLY use `analyze_emotion()`.

### "Why is ML optional?"

ML dependencies (transformers, torch) are heavy. Some deployments may not have them.
The keyword fallback ensures the system works everywhere.

### "Why is there a singleton pattern?"

Loading the ML model is expensive (RAM, time). The singleton ensures the model is loaded once and reused across all scene analyses.

### "Why does _ml_analyze truncate to 2000 characters?"

DistilRoBERTa has a 512 token limit. 2000 characters is a conservative estimate to avoid token overflow while capturing enough context.

### "Why does the output include 'method'?"

For debugging and evaluation. Phase 7 can track whether ML or keyword analysis was used, which affects metric interpretation.

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 2:
1. **Never fails**: Always returns valid emotion dict
2. **Graceful degradation**: ML → keyword → neutral
3. **Consistent output**: Same structure regardless of method
4. **Non-blocking**: Pipeline proceeds even if Phase 2 is disabled

### Invariants Maintained:
- Output always has `primary_emotion` (string)
- Output always has `primary_score` (float)
- Output always has `method` (string)
- Score values are always in [0, 1]

### What Would Break If Phase 2 Were Removed:
- Scene emotion field would be null
- Phase 4 would have less context for lighting decisions
- Phase 3 semantic RAG queries would have no emotion context
- Lighting would be more generic (script_type only)

**Note:** Phase 2 is optional. The system functions without it.
