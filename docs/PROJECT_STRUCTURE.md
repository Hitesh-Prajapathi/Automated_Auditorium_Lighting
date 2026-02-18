# Project Structure

> Reflects `baseline-rule-engine-stable` tag. Last updated: 2026-02-12.

```
Automated_Auditorium_Lighting/
│
├── contracts/                      # Phase 0: Schema Definitions (Locked)
│   ├── fixture_schema.json
│   ├── lighting_instruction_schema.json
│   ├── lighting_semantics_schema.json
│   └── scene_schema.json
│
├── phase_1/                        # Script Parsing & Scene Extraction
│   ├── __init__.py
│   ├── format_detector.py
│   ├── json_builder.py
│   ├── scene_segmenter.py
│   ├── text_cleaner.py
│   └── timestamp_generator.py
│
├── phase_2/                        # Emotion Analysis (DistilRoBERTa)
│   ├── __init__.py
│   └── emotion_analyzer.py
│
├── phase_3/                        # Dual RAG Knowledge Layer
│   ├── __init__.py
│   ├── rag_retriever.py            # Phase3Retriever (build_context_for_llm, retrieve_palette)
│   ├── ingestion/
│   │   └── knowledge_ingestion.py  # FAISS index builder
│   ├── knowledge/
│   │   ├── auditorium/
│   │   │   └── fixtures.json       # 54 fixture definitions
│   │   └── semantics/
│   │       └── baseline_semantics.json  # 7 lighting rules
│   ├── rag/
│   │   ├── auditorium/
│   │   │   ├── index.faiss         # Rebuilt for Python 3.11
│   │   │   └── index.pkl
│   │   └── lighting_semantics/
│   │       ├── index.faiss         # Rebuilt for Python 3.11
│   │       └── index.pkl
│   └── schemas/
│       ├── fixture_knowledge_schema.json
│       └── lighting_semantics_knowledge_schema.json
│
├── phase_4/                        # Lighting Decision Engine
│   ├── __init__.py
│   └── lighting_decision_engine.py # LLM chain + rule-based fallback
│
├── phase_5/                        # Simulation & Visualization
│   ├── __init__.py
│   ├── color_utils.py
│   ├── playback_engine.py
│   ├── scene_renderer.py
│   ├── server.py
│   ├── threejs_adapter.py
│   └── static/
│       └── index.html
│
├── phase_6/                        # Orchestration & Pipeline Control
│   ├── __init__.py
│   ├── batch_executor.py
│   ├── config_models.py            # PipelineConfig
│   ├── errors.py                   # HardFailureError
│   ├── pipeline_runner.py          # PipelineRunner (main orchestrator)
│   └── state_tracker.py
│
├── phase_7/                        # Evaluation & Metrics
│   ├── __init__.py
│   ├── metrics.py                  # MetricsEngine
│   ├── schemas.py                  # TraceEntry, TraceLog, RAGContextRef
│   ├── trace_logger.py             # TraceLogger
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── consistency.py          # Jaccard, determinism, drift, extract_group_ids
│   │   ├── coverage.py             # Group coverage, parameter diversity
│   │   └── stability.py            # Cross-run stability
│   └── experiment_configs/
│       ├── ablation.yaml
│       └── baseline.yaml
│
├── phase_8/                        # Hardware Execution (Future)
│   ├── __init__.py
│   ├── dmx_adapter.py
│   ├── lightkey_control.py
│   ├── lightkey_midi_control.py
│   ├── osc_sender.py
│   ├── setup_midi.py
│   └── mappings/
│       └── dmx_mappings.json
│
├── data/
│   ├── raw_scripts/                # Input scripts (.txt, .pdf, .docx)
│   ├── cleaned_scripts/            # Intermediate cleaned text
│   ├── segmented_scripts/          # Segmented scenes
│   ├── standardized_output/        # Phase 1 JSON output
│   ├── lighting_cues/              # Phase 4 lighting instructions
│   ├── traces/                     # Phase 7 trace logs
│   └── logs/                       # General logs
│
├── docs/                           # Documentation
│   ├── PROJECT_STRUCTURE.md        # This file
│   ├── DIRECTORY_STRUCTURE.md
│   ├── audit_1_to_6.md
│   ├── PHASE_1_STRUCTURE.md
│   ├── PHASE_2_STRUCTURE.md
│   ├── PHASE_3_README.md
│   ├── PHASE_4_STRUCTURE.md
│   ├── PHASE_6_STRUCTURE.md
│   └── workflow_knowledge/         # Detailed per-phase documentation
│       ├── PHASE_0_CONTRACTS.md
│       ├── PHASE_1_SCRIPT_INGESTION.md
│       ├── PHASE_2_EMOTION_ENRICHMENT.md
│       ├── PHASE_3_DUAL_RAG.md
│       ├── PHASE_4_LIGHTING_DECISION_ENGINE.md
│       ├── PHASE_5_SIMULATION_VISUALIZATION.md
│       ├── PHASE_6_ORCHESTRATION.md
│       └── PHASE_7_EVALUATION_METRICS.md
│
├── api/                            # Web API (Flask routes)
│   ├── __init__.py
│   ├── routes.py
│   └── websocket.py
│
├── static/                         # Web frontend assets
│   ├── css/style.css
│   └── js/
│       ├── viewer.js
│       └── websocket_client.js
│
├── templates/                      # HTML templates
│   ├── index.html
│   └── components/fixture_card.html
│
├── tests/                          # Test files
├── utils/                          # Utilities
│   ├── __init__.py
│   └── file_io.py
│
├── .env                            # Environment variables (OPENAI_API_KEY)
├── app.py                          # Flask application
├── config.py                       # Global configuration
├── main.py                         # Legacy entry point
├── main_phase2.py                  # Legacy Phase 2 entry point
├── main_visualize.py               # Legacy visualization entry point
├── requirements.txt                # Python dependencies
├── rules.md                        # Development rules
└── run_pipeline_test.py            # Pipeline entry point (current)
```

## Phase Summary

| Phase | Directory | Purpose | Failure Mode |
|-------|-----------|---------|--------------|
| 0 | `contracts/` | Schema definitions (locked) | N/A — static |
| 1 | `phase_1/` | Script parsing & scene extraction | **HARD FAIL** |
| 2 | `phase_2/` | Emotion analysis (DistilRoBERTa) | Soft — defaults to `neutral` |
| 3 | `phase_3/` | Dual FAISS RAG retrieval | **HARD FAIL** |
| 4 | `phase_4/` | Lighting decision engine | **HARD FAIL** after fallback |
| 5 | `phase_5/` | 3D simulation & visualization | Soft — log & continue |
| 6 | `phase_6/` | Pipeline orchestration | Controller — propagates |
| 7 | `phase_7/` | Trace logging & evaluation | Soft — log & continue |
| 8 | `phase_8/` | Hardware (DMX/Art-Net) | Not implemented |
