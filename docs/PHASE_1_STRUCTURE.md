# Phase 1: Script Parsing & Scene Extraction

## Overview

Phase 1 is the **PARSING LAYER** of the Automated Auditorium Lighting system. It converts raw script files into structured scene data for downstream processing.

**Key principle:** Transform unstructured text into structured JSON without interpretation.

---

## Architecture Position

```
[Phase 1] → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 7 → Phase 8
 Parsing   Emotion    RAG      Decision   Simulate  Evaluate  Hardware
```

### Inputs
- **Raw script files**: TXT, PDF, DOCX formats
- Various script styles: screenplay, dialogue, timestamped

### Outputs
- **Structured scenes**: List of scene dictionaries with content, timing, metadata

---

## File Structure

```
phase_1/
├── __init__.py              # Module exports
├── format_detector.py       # Script format detection
├── text_cleaner.py          # Text preprocessing
├── scene_segmenter.py       # Scene boundary detection
├── timestamp_generator.py   # Timing extraction/generation
└── json_builder.py          # Output JSON construction
```

---

## Core Components

### 1. Format Detector (`format_detector.py`)

Detects script format and extracts metadata.

```python
from phase_1 import detect_format

format_info = detect_format(raw_text)
# Returns: {
#     "timestamped": True/False,
#     "screenplay": True/False,
#     "dialogue_format": True/False,
#     "act_structure": True/False,
#     "estimated_format": "screenplay" | "dialogue_script" | "plain_text",
#     "complexity": "low" | "medium" | "high"
# }
```

**Detected Formats:**
| Format | Detection Criteria |
|--------|-------------------|
| `screenplay` | INT., EXT., FADE IN:, CUT TO: |
| `timestamped_script` | [00:30], 00:30:15, 10.5s |
| `dialogue_script` | CHARACTER: dialogue |
| `structured_json` | Valid JSON |
| `csv` | Comma-separated values |
| `plain_text` | Default fallback |

---

### 2. Text Cleaner (`text_cleaner.py`)

Preprocesses text while preserving structure.

```python
from phase_1 import clean_text

cleaned = clean_text(raw_text, preserve_structure=True)
```

**Functions:**
| Function | Purpose |
|----------|---------|
| `clean_text()` | Main cleaning with optional structure preservation |
| `extract_stage_directions()` | Extract (parenthetical) text |
| `remove_stage_directions()` | Remove (parenthetical) text |
| `extract_character_names()` | Extract ALL CAPS character names |
| `normalize_whitespace()` | Collapse multiple spaces |

---

### 3. Scene Segmenter (`scene_segmenter.py`)

Context-aware scene boundary detection.

```python
from phase_1 import segment_scenes

scenes = segment_scenes(cleaned_text, format_info)
# Returns: List[Dict] with scene content and metadata
```

**Segmentation Strategies:**
| Format | Strategy |
|--------|----------|
| Screenplay | Split by INT./EXT. headers |
| Dialogue | Split by speaker changes |
| Act Structure | Split by ACT/SCENE markers |
| Generic | Split by word count with sentence awareness |

**Output Schema:**
```python
{
    "header": "INT. LIVING ROOM - DAY",  # Optional
    "content": "Scene dialogue and action...",
    "type": "screenplay_scene" | "dialogue_block" | "segment",
    "location": "LIVING ROOM",  # Optional
    "speakers": ["CHARACTER_A", "CHARACTER_B"],  # Optional
    "word_count": 150
}
```

---

### 4. Timestamp Generator (`timestamp_generator.py`)

Generates or extracts timing information.

```python
from phase_1 import generate_timestamps, extract_timestamps

# Generate based on word count
timestamps = generate_timestamps(scenes)

# Extract from existing timestamps in text
timestamps = extract_timestamps(original_text, scenes)
```

**Timing Calculation:**
- Based on `WORDS_PER_MINUTE` config (default: 150)
- Scene transition buffer between scenes
- Minimum 2 seconds per scene

**Output Schema:**
```python
{
    "start": 0,      # Seconds
    "end": 30,       # Seconds
    "duration": 30,  # Seconds
    "extracted": True/False  # Was extracted vs generated
}
```

---

### 5. JSON Builder (`json_builder.py`)

Constructs final JSON output.

```python
from phase_1 import build_scene_json, build_complete_output, save_json

scene_json = build_scene_json(scene_id, scene_data, timestamp, emotion)
complete = build_complete_output(scenes, metadata)
save_json(complete, "output.json")
```

**Complete Output Schema:**
```python
{
    "metadata": {
        "generated_at": "2024-01-01T00:00:00",
        "total_scenes": 10,
        "total_duration_seconds": 300,
        "format_detected": "screenplay",
        "emotion_distribution": {...}
    },
    "scenes": [...]
}
```

---

## Configuration

From `config.py`:

| Config Key | Default | Description |
|------------|---------|-------------|
| `MAX_WORDS_PER_SCENE` | 500 | Maximum words before splitting |
| `MIN_WORDS_PER_SCENE` | 50 | Minimum words per scene |
| `WORDS_PER_MINUTE` | 150 | Speaking rate for timing |
| `SCENE_TRANSITION_BUFFER` | 2 | Seconds between scenes |
| `SCENE_MARKERS` | [...] | Scene header patterns |
| `JSON_INDENT` | 2 | JSON formatting |
| `TIMESTAMP_FORMAT` | "seconds" | Output format |

---

## Pipeline Flow

```
1. Read raw script file
2. detect_format() → format_info
3. clean_text() → cleaned_text
4. segment_scenes(cleaned_text, format_info) → scenes[]
5. generate_timestamps() or extract_timestamps() → timestamps[]
6. [Phase 2 enriches with emotion]
7. build_scene_json() for each scene
8. build_complete_output() → final JSON
9. save_json() → output file
```

---

## Hard Boundaries

Phase 1 **MUST NOT**:
- ❌ Analyze emotion (Phase 2)
- ❌ Query knowledge base (Phase 3)
- ❌ Generate lighting intent (Phase 4)
- ❌ Interpret scene meaning
- ❌ Modify scene content

Phase 1 **MUST**:
- ✅ Preserve original text faithfully
- ✅ Detect format automatically
- ✅ Generate consistent scene IDs
- ✅ Calculate accurate timing

---

## Usage Example

```python
from phase_1 import (
    detect_format,
    clean_text,
    segment_scenes,
    generate_timestamps
)

# Load raw script
with open("script.txt") as f:
    raw_text = f.read()

# Process
format_info = detect_format(raw_text)
cleaned = clean_text(raw_text, preserve_structure=True)
scenes = segment_scenes(cleaned, format_info)
timestamps = generate_timestamps(scenes)

# Combine
for i, (scene, ts) in enumerate(zip(scenes, timestamps)):
    scene["timing"] = ts
    scene["scene_id"] = f"scene_{i:03d}"

print(f"Parsed {len(scenes)} scenes")
```

---

## Error Handling

Phase 1 failures are **HARD FAIL** in Phase 6:
- Empty input → Raise exception
- Unreadable file → Raise exception
- No scenes detected → Fall back to generic segmentation
