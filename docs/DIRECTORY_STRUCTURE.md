# Automated Auditorium Lighting - Directory Structure

```
Automated_Auditorium_Lighting/
│
├── .agent/
│   └── KNOWLEDGE_BASE.md
│
├── api/
│   ├── __init__.py
│   ├── routes.py
│   └── websocket.py
│
├── contracts/
│   ├── fixture_schema.json
│   ├── lighting_instruction_schema.json
│   ├── lighting_semantics_schema.json
│   └── scene_schema.json
│
├── data/
│   ├── cleaned_scripts/
│   │   └── Script-20.txt
│   ├── lighting_cues/
│   │   └── Script-1_cues.json
│   ├── logs/
│   ├── raw_scripts/
│   │   ├── Script-1.txt
│   │   └── Script-10.pdf
│   ├── segmented_scripts/
│   │   └── Script-21.txt
│   └── standardized_output/
│       ├── Script-1.json
│       ├── Script-10_processed.json
│       ├── Script-1_processed.json
│       └── Script-20_processed.json
│
├── docs/
│   ├── PHASE_1_STRUCTURE.md
│   ├── PHASE_2_STRUCTURE.md
│   ├── PHASE_3_README.md
│   ├── PHASE_4_STRUCTURE.md
│   ├── PHASE_6_STRUCTURE.md
│   ├── PROJECT_STRUCTURE.md
│   ├── audit_1_to_6.md
│   └── DIRECTORY_STRUCTURE.md  ← (this file)
│
├── phase_1/                    # Script Parsing & Scene Extraction
│   ├── __init__.py
│   ├── format_detector.py
│   ├── json_builder.py
│   ├── scene_segmenter.py
│   ├── text_cleaner.py
│   └── timestamp_generator.py
│
├── phase_2/                    # Emotion Analysis
│   ├── __init__.py
│   └── emotion_analyzer.py
│
├── phase_3/                    # Dual RAG (Knowledge Layer)
│   ├── __init__.py
│   ├── rag_retriever.py
│   ├── ingestion/
│   │   └── knowledge_ingestion.py
│   ├── knowledge/
│   │   ├── auditorium/
│   │   │   └── fixtures.json
│   │   └── semantics/
│   │       └── baseline_semantics.json
│   ├── rag/
│   │   ├── auditorium/
│   │   │   ├── index.faiss
│   │   │   └── index.pkl
│   │   └── lighting_semantics/
│   │       ├── index.faiss
│   │       └── index.pkl
│   └── schemas/
│       ├── fixture_knowledge_schema.json
│       └── lighting_semantics_knowledge_schema.json
│
├── phase_4/                    # Lighting Decision Engine
│   ├── __init__.py
│   └── lighting_decision_engine.py
│
├── phase_5/                    # Simulation & Visualization
│   ├── __init__.py
│   ├── README.md
│   ├── IMPLEMENTATION_PLAN.md
│   ├── color_utils.py
│   ├── playback_engine.py
│   ├── scene_renderer.py
│   ├── server.py
│   ├── threejs_adapter.py
│   └── static/
│       └── index.html
│
├── phase_6/                    # Orchestration & Pipeline Control
│   ├── __init__.py
│   ├── README.md
│   ├── batch_executor.py
│   ├── config_models.py
│   ├── errors.py
│   ├── pipeline_runner.py
│   └── state_tracker.py
│
├── phase_7/                    # Logging & Evaluation
│   ├── __init__.py
│   ├── README.md
│   ├── demo.py
│   ├── metrics.py
│   ├── schemas.py
│   ├── trace_logger.py
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── consistency.py
│   │   ├── coverage.py
│   │   └── stability.py
│   └── experiment_configs/
│       ├── ablation.yaml
│       └── baseline.yaml
│
├── phase_8/                    # Hardware Execution (Future)
│   ├── __init__.py
│   ├── dmx_adapter.py
│   ├── lightkey_control.py
│   ├── lightkey_midi_control.py
│   ├── osc_sender.py
│   ├── setup_midi.py
│   └── mappings/
│       └── dmx_mappings.json
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── viewer.js
│       └── websocket_client.js
│
├── templates/
│   ├── index.html
│   └── components/
│       └── fixture_card.html
│
├── tests/
│
├── utils/
│   ├── __init__.py
│   └── file_io.py
│
├── app.py
├── config.py
├── main.py
├── main_phase2.py
├── main_visualize.py
├── README.md
├── requirements.txt
└── rules.md
```

---

## Phase Summary

| Phase | Directory | Purpose |
|-------|-----------|---------|
| 0 | `contracts/` | Schema definitions (locked) |
| 1 | `phase_1/` | Script parsing & scene extraction |
| 2 | `phase_2/` | Emotion analysis (optional) |
| 3 | `phase_3/` | Dual RAG knowledge retrieval |
| 4 | `phase_4/` | Lighting decision engine |
| 5 | `phase_5/` | Simulation & visualization |
| 6 | `phase_6/` | Orchestration & pipeline control |
| 7 | `phase_7/` | Logging & evaluation |
| 8 | `phase_8/` | Hardware execution (future) |
