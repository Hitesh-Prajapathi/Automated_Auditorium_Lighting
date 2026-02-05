# Phase 2: Emotion Analysis

## Overview

Phase 2 is the **EMOTION LAYER** of the Automated Auditorium Lighting system. It enriches scene data with emotional context using ML models or keyword fallback.

**Key principle:** Add emotional metadata without modifying scene content.

---

## Architecture Position

```
Phase 1 → [Phase 2] → Phase 3 → Phase 4 → Phase 5 → Phase 7 → Phase 8
 Parsing   Emotion    RAG      Decision   Simulate  Evaluate  Hardware
```

### Inputs
- **Scene content**: Text from Phase 1

### Outputs
- **Emotion analysis**: Primary/secondary emotions, confidence scores

---

## File Structure

```
phase_2/
├── __init__.py           # Module exports (analyze_emotion)
└── emotion_analyzer.py   # Core emotion analysis logic
```

---

## Core Components

### EmotionAnalyzer Class

The main class for emotion analysis with dual-mode operation.

```python
from phase_2 import analyze_emotion

result = analyze_emotion("A celebration begins with laughter!")
# Returns: {
#     "primary_emotion": "joy",
#     "secondary_emotion": "excitement",
#     "confidence": 0.85,
#     "all_emotions": {...},
#     "method": "ml" | "keyword"
# }
```

---

## Analysis Modes

### 1. ML Mode (Default if Available)

Uses DistilRoBERTa transformer model for emotion classification.

| Aspect | Details |
|--------|---------|
| Model | `j-hartmann/emotion-english-distilroberta-base` |
| Library | HuggingFace Transformers |
| Emotions | 7 classes |
| Speed | ~0.1s per scene (GPU) |

**Detected Emotions (ML):**
- anger
- disgust
- fear
- joy
- neutral
- sadness
- surprise

### 2. Keyword Mode (Fallback)

Pure Python keyword matching when ML unavailable.

| Aspect | Details |
|--------|---------|
| Dependencies | None |
| Speed | Instant |
| Accuracy | Lower than ML |

**Keyword Categories:**
```python
{
    "joy": ["happy", "excited", "celebrate", "laugh", "wonderful"],
    "sadness": ["sad", "crying", "tears", "mourn", "grief"],
    "anger": ["angry", "furious", "rage", "hate", "furious"],
    "fear": ["afraid", "scared", "terror", "panic", "dread"],
    "surprise": ["shocked", "amazed", "astonished", "unexpected"],
    "disgust": ["disgusted", "revolted", "repulsed", "sick"],
    "love": ["love", "adore", "cherish", "devotion", "affection"],
    "tension": ["suspense", "anxiety", "nervous", "uneasy"]
}
```

---

## Output Schema

```python
{
    "primary_emotion": "joy",          # Main detected emotion
    "secondary_emotion": "excitement", # Secondary emotion (if any)
    "confidence": 0.85,                # 0.0 - 1.0
    "all_emotions": {                  # All scores
        "joy": 0.85,
        "sadness": 0.05,
        "anger": 0.02,
        ...
    },
    "method": "ml",                    # "ml" or "keyword"
    "threshold_met": True              # Confidence > EMOTION_THRESHOLD
}
```

---

## Configuration

From `config.py`:

| Config Key | Default | Description |
|------------|---------|-------------|
| `EMOTION_MODEL` | "distilroberta" | Model name |
| `EMOTION_THRESHOLD` | 0.4 | Minimum confidence |
| `USE_ML_EMOTION` | True | Use ML if available |

---

## API Reference

### Main Functions

```python
# Simple analysis (recommended)
from phase_2 import analyze_emotion
result = analyze_emotion(text)

# Using singleton instance
from phase_2 import get_analyzer
analyzer = get_analyzer()
result = analyzer.analyze(text)

# Creating new instance
from phase_2.emotion_analyzer import EmotionAnalyzer
analyzer = EmotionAnalyzer(use_ml=False)  # Force keyword mode
result = analyzer.analyze(text)
```

### EmotionAnalyzer Methods

| Method | Description |
|--------|-------------|
| `analyze(text)` | Main analysis method |
| `_ml_analyze(text)` | ML-based analysis |
| `_keyword_analyze(text)` | Keyword-based fallback |
| `_neutral_response()` | Default neutral return |

---

## Failure Handling

Phase 2 is **OPTIONAL** in the pipeline:

| Scenario | Behavior |
|----------|----------|
| ML not installed | Use keyword mode |
| Empty text | Return neutral |
| Analysis error | Return neutral, log warning |
| Phase 2 disabled | Skip, use neutral |

**Neutral Response:**
```python
{
    "primary_emotion": "neutral",
    "secondary_emotion": None,
    "confidence": 0.0,
    "all_emotions": {"neutral": 1.0},
    "method": "fallback"
}
```

---

## Integration with Pipeline

Phase 6 calls Phase 2 like this:

```python
from phase_2 import analyze_emotion

# For each scene from Phase 1
scene_text = scene.get("content", "")
emotion_analysis = analyze_emotion(scene_text)
scene["emotion"] = emotion_analysis
```

---

## Hard Boundaries

Phase 2 **MUST NOT**:
- ❌ Parse scripts (Phase 1)
- ❌ Query knowledge base (Phase 3)
- ❌ Generate lighting intent (Phase 4)
- ❌ Modify scene structure
- ❌ Make decisions based on emotion

Phase 2 **MUST**:
- ✅ Return consistent schema
- ✅ Handle empty input gracefully
- ✅ Indicate analysis method used
- ✅ Provide confidence scores

---

## Performance

| Mode | Speed | Accuracy |
|------|-------|----------|
| ML (GPU) | ~100ms/scene | High |
| ML (CPU) | ~500ms/scene | High |
| Keyword | ~1ms/scene | Medium |

---

## Usage Examples

### Basic Usage

```python
from phase_2 import analyze_emotion

# Analyze text
result = analyze_emotion("The crowd erupts in thunderous applause!")
print(f"Emotion: {result['primary_emotion']}")  # joy
print(f"Confidence: {result['confidence']}")    # 0.82
```

### Force Keyword Mode

```python
from phase_2.emotion_analyzer import EmotionAnalyzer

analyzer = EmotionAnalyzer(use_ml=False)
result = analyzer.analyze("A dark and stormy night...")
print(f"Method: {result['method']}")  # keyword
```

### Batch Processing

```python
from phase_2 import analyze_emotion

scenes = [scene1, scene2, scene3]
for scene in scenes:
    scene["emotion"] = analyze_emotion(scene["content"])
```

---

## Dependencies

**Required:**
- Python 3.8+

**Optional (for ML mode):**
- transformers
- torch

```bash
pip install transformers torch
```
