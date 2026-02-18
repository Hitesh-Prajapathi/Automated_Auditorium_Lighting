# Architecture Audit — Phases 1 to 7

> Reflects `baseline-rule-engine-stable` tag. Last updated: 2026-02-12.

## Audit Summary

All phases (1–7) pass in deterministic rule-based mode. Phase 8 (hardware) is not implemented.

| Phase | Status | Notes |
|-------|--------|-------|
| 1 — Parsing | ✅ Stable | 10 scenes from Script-1.txt |
| 2 — Emotion | ✅ Stable | DistilRoBERTa, soft-fail to neutral |
| 3 — RAG | ✅ Rebuilt | FAISS indexes rebuilt for Python 3.11 |
| 4 — Decision | ✅ Rule-based | LLM path disabled (SDK conflict) |
| 5 — Simulation | ✅ Stable | Headless rendering |
| 6 — Orchestration | ✅ Stable | Controls all phases |
| 7 — Evaluation | ✅ Wired | TraceLogger + MetricsEngine active |

---

## Phase 1 — Script Parsing & Scene Extraction

**Location**: `phase_1/`

**Purpose**: Parse raw script files (.txt, .pdf, .docx), detect format, segment into scenes, generate timestamps, and build standardized JSON.

**Components**:
- `format_detector.py` — Detects screenplay, stage play, or generic format
- `text_cleaner.py` — Normalizes whitespace, encoding, line breaks
- `scene_segmenter.py` — Splits text into scenes using heading patterns
- `timestamp_generator.py` — Estimates timestamps from word count
- `json_builder.py` — Assembles final JSON with metadata

**Input**: Raw script file path (`.txt`, `.pdf`, `.docx`)
**Output**: List of scene dicts with `content`, `timing`, `metadata`

**Failure Mode**: HARD FAIL — pipeline cannot continue without scenes.

**Limitation**: Scene IDs default to `unknown`; parser does not generate unique scene identifiers.

---

## Phase 2 — Emotion Analysis

**Location**: `phase_2/`

**Purpose**: Classify the dominant emotion of each scene using ML.

**Components**:
- `emotion_analyzer.py` — Wraps HuggingFace `j-hartmann/emotion-english-distilroberta-base`

**Input**: Scene text (string)
**Output**: Emotion label (e.g., `neutral`, `fear`, `surprise`, `joy`, `anger`, `sadness`, `disgust`)

**Failure Mode**: SOFT — defaults to `neutral` if model fails. Pipeline continues.

**Baseline Results**: Script-1.txt detects `neutral` (6 scenes), `fear` (3 scenes), `surprise` (1 scene).

---

## Phase 3 — Dual RAG Knowledge Retrieval

**Location**: `phase_3/`

**Purpose**: Retrieve relevant fixture specifications and lighting semantics using FAISS vector search.

**Components**:
- `rag_retriever.py` — `Phase3Retriever` class with three methods:
  - `retrieve_auditorium_context(query, k)` → fixture metadata
  - `retrieve_semantics_context(emotion, script_type, k)` → semantics rules
  - `build_context_for_llm(emotion, scene_text)` → merged context string (adapter)
  - `retrieve_palette(emotion)` → palette dict for Phase 4 fallback (adapter)
- `ingestion/knowledge_ingestion.py` — FAISS index builder

**FAISS Indexes** (rebuilt for Python 3.11):

| Index | Documents | Source |
|-------|-----------|--------|
| Auditorium | 54 fixtures | `knowledge/auditorium/fixtures.json` |
| Semantics | 7 rules | `knowledge/semantics/baseline_semantics.json` |

**Input**: Emotion string, scene text
**Output**: RAG context string (1891–2132 chars per scene in baseline)

**Failure Mode**: HARD FAIL — pipeline depends on RAG context.

---

## Phase 4 — Lighting Decision Engine

**Location**: `phase_4/`

**Purpose**: Generate `LightingInstruction` for each scene using either LLM (GenAI mode) or rule-based logic (baseline mode).

**Components**:
- `lighting_decision_engine.py`:
  - `LightingDecisionEngine` — main class
  - `_create_llm_chain()` — LangChain chain (ChatOpenAI + PydanticOutputParser)
  - `_rule_based_generation()` — deterministic fallback
  - `SimpleRetriever` — hardcoded palette fallback (used if Phase 3 retriever unavailable)

**Modes**:

| Mode | Config | Status |
|------|--------|--------|
| Rule-based (baseline) | `use_llm=False` | ✅ Active |
| GenAI (LLM) | `use_llm=True` | ⚠ Blocked by SDK conflict |

**LLM Safe Limits** (in `config.py`):
- `LLM_TEMPERATURE = 0.0`
- `LLM_MAX_TOKENS = 500`
- `FALLBACK_TO_RULES = True`

**Input**: Enriched scene dict, RAG context string
**Output**: `LightingInstruction` dict with `groups` (2 per scene in baseline: `front_wash`, `back_light`)

**Failure Mode**: HARD FAIL after fallback attempts. If LLM fails and `FALLBACK_TO_RULES=True`, tries rule-based. If both fail, pipeline halts.

**Limitation**: Rule-based mode uses only 2 of 5 available groups (coverage = 0.4).

---

## Phase 5 — Simulation & Visualization

**Location**: `phase_5/`

**Purpose**: Render lighting instructions into a visual simulation.

**Components**:
- `playback_engine.py` — Sequencing engine for lighting cues
- `scene_renderer.py` — Renders scenes (headless or visual)
- `color_utils.py` — Color conversion utilities (RGB, HSL, temperature)
- `threejs_adapter.py` — Three.js data adapter
- `server.py` — Flask server for browser-based visualization

**Input**: List of `LightingInstruction` dicts
**Output**: Rendered simulation (headless in pipeline mode)

**Failure Mode**: SOFT — non-fatal, log and continue.

**Boundary**: Phase 5 does NOT call LLMs, modify lighting intent, or generate new instructions.

---

## Phase 6 — Orchestration & Pipeline Control

**Location**: `phase_6/`

**Purpose**: Orchestrate all phases in the correct order, manage state, handle failures.

**Components**:
- `pipeline_runner.py` — `PipelineRunner.run(script_path)` orchestrates Phases 1→2→3→4→5→7
- `config_models.py` — `PipelineConfig` (enable_phase_5, enable_phase_7, use_llm)
- `state_tracker.py` — Phase state tracking and timing
- `errors.py` — `HardFailureError` for fatal phase failures
- `batch_executor.py` — Multi-script batch execution

**Input**: Script file path + `PipelineConfig`
**Output**: `PipelineResult` with per-phase results

**Boundary**: Phase 6 does NOT modify outputs from any phase. It only routes data and manages state.

---

## Phase 7 — Evaluation & Metrics

**Location**: `phase_7/`

**Purpose**: Observe and log execution traces, compute research-grade metrics.

**Components**:
- `trace_logger.py` — `TraceLogger.log_decision(scene, instruction)` creates `TraceEntry` with input/output hashes
- `metrics.py` — `MetricsEngine` computes coverage, diversity, drift, determinism, cross-run stability
- `schemas.py` — Pydantic models: `TraceEntry`, `TraceLog`, `RAGContextRef`
- `evaluation/consistency.py` — Jaccard similarity, determinism score, drift score, `extract_group_ids`
- `evaluation/coverage.py` — Group coverage, parameter diversity
- `evaluation/stability.py` — Cross-run stability metrics

**Pipeline Integration** (in `pipeline_runner.py`):
1. After all scenes processed, `TraceLogger.log_decision()` is called per scene
2. `TraceLogger.save()` writes to `data/traces/trace_<uuid>.json`
3. `MetricsEngine.generate_report()` computes drift, coverage, diversity

**Baseline Metrics**:

| Metric | Value |
|--------|-------|
| Drift Score | 0.333 |
| Coverage | 0.4 (2/5 groups) |
| Diversity (intensity range) | 0.075–0.24 |
| Transition types | 1 (fade) |
| Colors per scene | 1 |

**Boundary**: Phase 7 is OBSERVATIONAL ONLY. It does NOT:
- Import from Phase 4 or other phases
- Call LLM APIs
- Modify lighting intent
- Influence execution

**Failure Mode**: SOFT — non-fatal, log and continue. Pipeline succeeds even if Phase 7 fails.

---

## Known Issues (Baseline)

| Issue | Phase | Status |
|-------|-------|--------|
| `langchain-openai==0.1.6` proxy arg conflict | 4 | Blocks LLM mode |
| Scene IDs default to `unknown` | 1 → 7 | Metrics lack identifiers |
| Coverage 0.4 (2/5 groups) | 4 | Expected in rule-based mode |
| HuggingFace `resume_download` deprecation | 2 | Cosmetic warning |
