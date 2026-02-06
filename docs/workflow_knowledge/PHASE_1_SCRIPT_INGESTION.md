# PHASE 1: SCRIPT INGESTION & STRUCTURING

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 1 converts **raw theatrical scripts** (various formats) into **structured Scene JSON** that can be processed by downstream phases. It is the first processing phase after contracts.

### What Problem It Solves
Scripts come in many formats: screenplays, dialogue scripts, timestamped cue sheets, plain text. Phase 1 normalizes all of these into a single canonical Scene JSON structure defined by the Phase 0 contract.

### What Question It Answers
> "What are the distinct scenes in this script, and what is their timing and content?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_1/`

Contains 6 files forming a linear processing pipeline.

---

### File: `phase_1/__init__.py`

**Why This File Exists:**
Exports the public API of Phase 1 for external consumption.

**How It Is Used:**
Imported by Phase 6 (orchestrator) and `main.py` to access Phase 1 functions.

**When It Is Imported:**
```python
from phase_1 import (
    detect_format,
    clean_text,
    segment_scenes,
    generate_timestamps,
    build_scene_json,
    build_complete_output
)
```

**Who Calls It:**
- `phase_6/pipeline_runner.py` (orchestration)
- `main.py` (direct execution)

**Exports:**
- `detect_format` — from `format_detector.py`
- `clean_text`, `extract_stage_directions` — from `text_cleaner.py`
- `segment_scenes` — from `scene_segmenter.py`
- `generate_timestamps`, `extract_timestamps` — from `timestamp_generator.py`
- `build_scene_json`, `build_complete_output` — from `json_builder.py`

---

### File: `phase_1/format_detector.py`

**Why This File Exists:**
Analyzes raw text to determine what script format it is (screenplay, dialogue, timestamped, etc.).

**How It Is Used:**
Called first in the pipeline to determine how to segment the script.

**When It Is Imported:**
By `__init__.py` and internally by `scene_segmenter.py`.

**Who Calls It:**
- Phase 6 pipeline runner
- `main.py`

---

### File: `phase_1/text_cleaner.py`

**Why This File Exists:**
Cleans and normalizes raw text while preserving important structural elements.

**How It Is Used:**
Called after format detection, before segmentation.

**When It Is Imported:**
By `__init__.py`.

**Who Calls It:**
- Phase 6 pipeline runner
- `main.py`

---

### File: `phase_1/scene_segmenter.py`

**Why This File Exists:**
Splits cleaned text into discrete scenes based on detected format.

**How It Is Used:**
Takes format info and text, returns list of scene dictionaries.

**When It Is Imported:**
By `__init__.py`.

**Who Calls It:**
- Phase 6 pipeline runner
- `main.py`

---

### File: `phase_1/timestamp_generator.py`

**Why This File Exists:**
Generates or extracts timing information for each scene.

**How It Is Used:**
Either extracts existing timestamps from text or calculates them based on word count.

**When It Is Imported:**
By `__init__.py` and `json_builder.py`.

**Who Calls It:**
- Phase 6 pipeline runner
- `main.py`
- `json_builder.py` (for formatting)

---

### File: `phase_1/json_builder.py`

**Why This File Exists:**
Assembles the final Scene JSON structure from all processed components.

**How It Is Used:**
Takes scene data, timestamps, and emotion analysis → outputs contract-compliant JSON.

**When It Is Imported:**
By `__init__.py`.

**Who Calls It:**
- Phase 6 pipeline runner
- `main.py`

**Note:** This file has a stale import (`from pipeline.timestamp_generator import format_timestamp`) that should reference `phase_1.timestamp_generator`.

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

Phase 1 contains **no classes**. All logic is in pure functions.

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `format_detector.py`

#### `detect_format(text: str) -> dict`

**Exact Responsibility:**
Analyzes raw text to determine script format and characteristics.

**Input Parameters:**
- `text` (str): Raw script text

**Output Values:**
```python
{
    "timestamped": bool,      # Has timing markers
    "screenplay": bool,       # Has INT./EXT. markers
    "stage_directions": bool, # Has parenthetical directions
    "dialogue_format": bool,  # Has CHARACTER: pattern
    "act_structure": bool,    # Has ACT/SCENE markers
    "is_json": bool,          # Already structured JSON
    "is_csv": bool,           # CSV format
    "estimated_format": str,  # One of: structured_json, csv, screenplay, timestamped_script, dialogue_script, plain_text
    "complexity": str         # low, medium, high
}
```

**Side Effects:** None

**Failure Modes:** 
- Cannot fail (returns default values for unrecognized formats)

**Where Called From:**
- `scene_segmenter.segment_scenes()` (uses output)
- `main.py` (direct call)
- Phase 6 pipeline

---

#### `_estimate_format(screenplay, timestamped, is_json, is_csv, dialogue_format) -> str`

**Exact Responsibility:**
Helper to determine primary format type.

**Called By:** `detect_format()` only

---

#### `_estimate_complexity(text: str) -> str`

**Exact Responsibility:**
Estimates script complexity based on word count.

**Returns:** `"low"` (<3000), `"medium"` (3000-10000), `"high"` (>10000)

---

### `text_cleaner.py`

#### `clean_text(text: str, preserve_structure: bool = True) -> str`

**Exact Responsibility:**
Cleans text while optionally preserving structural markers.

**Input Parameters:**
- `text` (str): Raw text
- `preserve_structure` (bool): Keep scene markers (default: True)

**Output Values:**
Cleaned string with normalized whitespace and removed special characters.

**Side Effects:** None

**Failure Modes:** Returns empty string for None/empty input

---

#### `extract_stage_directions(text: str) -> list[str]`

**Exact Responsibility:**
Extracts text in parentheses (stage directions) as separate list.

**Returns:** List of direction strings

---

#### `remove_stage_directions(text: str) -> str`

**Exact Responsibility:**
Returns text with parenthetical content removed.

---

#### `extract_character_names(text: str) -> list[str]`

**Exact Responsibility:**
Finds ALL CAPS character names followed by colons.

**Returns:** Deduplicated list of character names

---

#### `normalize_whitespace(text: str) -> str`

**Exact Responsibility:**
Collapses all whitespace to single spaces.

---

### `scene_segmenter.py`

#### `segment_scenes(text: str, format_info: dict) -> list[dict]`

**Exact Responsibility:**
Main entry point for scene segmentation. Routes to format-specific segmenters.

**Input Parameters:**
- `text` (str): Cleaned script text
- `format_info` (dict): Output from `detect_format()`

**Output Values:**
```python
[
    {
        "content": str,      # Scene text
        "type": str,         # screenplay_scene, dialogue_block, act_segment, segment
        "header": str,       # Optional: scene header
        "location": str,     # Optional: extracted location
        "speakers": list,    # Optional: character names
        "word_count": int    # Optional: word count
    }
]
```

**Routing Logic:**
- `format_info["screenplay"]` → `_segment_screenplay()`
- `format_info["dialogue_format"]` → `_segment_dialogue()`
- `format_info["act_structure"]` → `_segment_by_acts()`
- Otherwise → `_segment_generic()`

---

#### `_segment_screenplay(text: str) -> list[dict]`

**Exact Responsibility:**
Segments by scene headers (INT., EXT., INTERIOR, EXTERIOR).

Uses markers from `config.SCENE_MARKERS`.

Falls back to `_segment_generic()` if no scenes found.

---

#### `_segment_dialogue(text: str) -> list[dict]`

**Exact Responsibility:**
Segments by speaker changes with word count limits.

Uses `config.MAX_WORDS_PER_SCENE` to chunk.

---

#### `_segment_by_acts(text: str) -> list[dict]`

**Exact Responsibility:**
Segments by ACT/SCENE markers. Further subdivides long acts.

---

#### `_segment_generic(text: str, max_words: int) -> list[dict]`

**Exact Responsibility:**
Fallback: segments by word count with sentence awareness.

Uses `config.MAX_WORDS_PER_SCENE` and `config.MIN_WORDS_PER_SCENE`.

---

### `timestamp_generator.py`

#### `generate_timestamps(scenes: list) -> list[dict]`

**Exact Responsibility:**
Creates timing based on word count and speaking speed.

**Input Parameters:**
- `scenes` (list): Scene dictionaries with "content" field

**Output Values:**
```python
[
    {
        "start": float,    # Start time in seconds
        "end": float,      # End time in seconds
        "duration": float  # Duration in seconds
    }
]
```

Uses `config.WORDS_PER_MINUTE` and `config.SCENE_TRANSITION_BUFFER`.

---

#### `extract_timestamps(text: str, scenes: list) -> list[dict]`

**Exact Responsibility:**
Attempts to extract existing timestamps from source text. Falls back to generation if not found.

Adds `"extracted": True/False` flag.

---

#### `_parse_timestamp(match, pattern_type: str) -> int|None`

**Exact Responsibility:**
Converts regex match to seconds.

Handles: `[00:30]`, `00:30:15`, `10.5s` formats.

---

#### `_calculate_duration(text: str) -> int`

**Exact Responsibility:**
Word count ÷ speaking rate → seconds.

Minimum: 2 seconds.

---

#### `format_timestamp(seconds: int, format_type: str) -> str`

**Exact Responsibility:**
Formats seconds to display format.

Options: `"seconds"` (10.5s), `"timecode"` (00:00:30), `"short"` (00:30)

---

### `json_builder.py`

#### `build_scene_json(scene_id, scene_data, timestamp, emotion_analysis) -> dict`

**Exact Responsibility:**
Builds a single Scene JSON object conforming to contract.

**Input Parameters:**
- `scene_id` (str): Unique identifier
- `scene_data` (dict): From segmenter
- `timestamp` (dict): From timestamp generator
- `emotion_analysis` (dict): From Phase 2 (or empty)

**Output Values:**
```python
{
    "scene_id": str,
    "timing": {
        "start_time": float,
        "end_time": float,
        "duration": float
    },
    "content": {
        "text": str,
        "word_count": int,
        "type": str,
        # Optional: header, location, speakers, speaker_count
    },
    "emotion": dict
}
```

---

#### `build_complete_output(scenes: list, metadata: dict) -> dict`

**Exact Responsibility:**
Wraps all scenes in final output structure with metadata.

**Output Values:**
```python
{
    "metadata": {
        "generated_at": str,
        "generator_version": str,
        "total_scenes": int,
        "total_duration_seconds": float,
        "total_duration_formatted": str,
        "format_detected": str,
        "source_file": str,
        "emotion_distribution": dict
    },
    "scenes": list
}
```

---

#### `_calculate_emotion_distribution(scenes: list) -> dict`

**Exact Responsibility:**
Aggregates emotion statistics across all scenes.

Returns counts, percentages, and dominant emotion.

---

#### `save_json(data, filepath)` / `save_json_compact(data, filepath)`

**Exact Responsibility:**
File output utilities.

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1 EXECUTION FLOW                                         │
└─────────────────────────────────────────────────────────────────┘

1. INPUT: Raw script text (from file or string)
          │
          ▼
2. detect_format(text)
   └── Returns format_info dict
          │
          ▼
3. clean_text(text, preserve_structure=True)
   └── Returns cleaned text
          │
          ▼
4. segment_scenes(cleaned_text, format_info)
   └── Routes to appropriate segmenter
   └── Returns list of scene dicts
          │
          ▼
5. generate_timestamps(scenes) OR extract_timestamps(text, scenes)
   └── Returns list of timestamp dicts
          │
          ▼
6. FOR EACH scene:
   └── build_scene_json(scene_id, scene, timestamp, emotion={})
          │
          ▼
7. build_complete_output(scenes, metadata)
   └── Returns final JSON structure
          │
          ▼
8. OUTPUT: Structured Scene JSON (contract-compliant)
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Input: Raw Script Text
- Plain text string
- No structure requirements
- May contain timestamps, markers, or be plain prose

### Intermediate: Format Info
```python
{
    "timestamped": bool,
    "screenplay": bool,
    "stage_directions": bool,
    "dialogue_format": bool,
    "act_structure": bool,
    "is_json": bool,
    "is_csv": bool,
    "estimated_format": str,
    "complexity": str
}
```

### Intermediate: Scene Segment
```python
{
    "content": str,
    "type": str,
    "header": str,        # Optional
    "location": str,      # Optional
    "speakers": list,     # Optional
    "word_count": int     # Optional
}
```

### Output: Scene JSON (Contract-Compliant)
See Phase 0 `scene_schema.json` for canonical definition.

---

## 7️⃣ FAILURE BEHAVIOR

### Format Detection Fails
- Returns default format (`plain_text`)
- Segmenter falls back to generic word-count segmentation
- **Execution continues**

### Segmentation Finds No Scenes
- All segmenters fall back to `_segment_generic()`
- If still empty, returns single scene with full text
- **Execution continues**

### Timestamp Extraction Fails
- Falls back to `generate_timestamps()` based on word count
- Adds `"extracted": False` flag
- **Execution continues**

### JSON Building Fails
- Would raise exception (structural issue in input data)
- **Would halt pipeline** — Phase 6 catches as HardFailureError

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 1 MUST NOT Do:
- ❌ Must NOT analyze emotions (that's Phase 2)
- ❌ Must NOT query RAG (that's Phase 3)
- ❌ Must NOT generate lighting intent (that's Phase 4)
- ❌ Must NOT infer what lighting SHOULD be (intent inference is Phase 4's job)

### What Phase 1 MUST Do:
- ✅ Preserve explicit lighting cues verbatim in `explicit_lighting` array
- ✅ Output contract-compliant Scene JSON
- ✅ Handle all input formats gracefully

### How Phase Isolation Is Enforced:
- No imports from Phase 2, 3, 4, 5, 6, 7, 8
- Only imports: `config.py`, standard library, `datetime`
- One stale import: `json_builder.py` imports from `pipeline.timestamp_generator` (should be `phase_1.timestamp_generator`)

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why does Phase 1 accept emotion_analysis as a parameter in build_scene_json?"

Phase 1 can be called before or after Phase 2. When called from the full pipeline, emotion analysis is passed in. When called standalone, an empty dict is used.

### "Why is there both generate_timestamps and extract_timestamps?"

- `extract_timestamps`: Tries to find existing timestamps in the source (preserves author intent)
- `generate_timestamps`: Calculates timing from word count (fallback)

The system prefers extracted timestamps when available.

### "Why does _segment_generic use sentence awareness?"

Scenes should end at sentence boundaries for narrative coherence. Word limits are targets, not hard stops.

### "Why is there a stale import to pipeline.timestamp_generator?"

This is a remnant from before the phase directory restructuring. It should be fixed but has not broken because the function is also available via the published API.

### "Why does format_info have so many boolean flags?"

Multiple flags can be true simultaneously. A script can be both a screenplay AND timestamped. The `estimated_format` picks the primary type, but flags preserve detail.

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 1:
1. **Format agnostic**: Accepts any text-based script format
2. **Contract compliance**: Outputs valid Scene JSON per schema
3. **Timing guarantee**: Every scene has start/end times
4. **Graceful degradation**: Falls back to generic processing if format unknown

### Invariants Maintained:
- Output always has `scene_id`, `text`, `time_window`
- `emotion` field is always present (null or object)
- Scene order matches input order
- No scenes are lost (worst case: single scene with full text)

### What Would Break If Phase 1 Were Removed:
- No structured scene data for downstream phases
- Phase 4 would have no input to process
- Pipeline would have no concept of timing or scene boundaries
