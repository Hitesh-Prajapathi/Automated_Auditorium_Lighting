# Automated Auditorium Lighting - Project Structure

```text
.
├── PHASE_3_README.md
├── README.md
├── api
│   ├── __init__.py
│   ├── routes.py
│   └── websocket.py
├── app.py
├── bind_osc.py
├── config.py
├── data
│   ├── auditorium_knowledge
│   │   ├── dmx_mappings.json
│   │   ├── fixtures.json
│   │   ├── mood_palettes.json
│   │   └── stage_geometry.json
│   ├── cleaned_scripts
│   │   └── Script-20.txt
│   ├── knowledge
│   │   ├── auditorium
│   │   │   └── fixtures.json
│   │   ├── schemas
│   │   │   ├── fixture_schema.json
│   │   │   └── lighting_semantics_schema.json
│   │   └── semantics
│   │       └── baseline_semantics.json
│   ├── lighting_cues
│   │   ├── Script-1_cues.json
│   │   └── Script-1_dmx.json
│   ├── raw_scripts
│   │   ├── Script-1.txt
│   │   └── Script-10.pdf
│   ├── segmented_scripts
│   │   └── Script-21.txt
│   └── standardized_output
│       ├── Script-1.json
│       ├── Script-10_processed.json
│       ├── Script-1_processed.json
│       └── Script-20_processed.json
├── lightkey_control.py
├── main.py
├── main_phase2.py
├── main_visualize.py
├── pipeline
│   ├── __init__.py
│   ├── cue_generator.py
│   ├── cue_validator.py
│   ├── dmx_converter.py
│   ├── emotion_analyzer.py
│   ├── format_detector.py
│   ├── json_builder.py
│   ├── knowledge_ingestion.py  <-- [Phase 3 Builder]
│   ├── rag_retriever.py        <-- [Phase 3 Interface]
│   ├── scene_segmenter.py
│   ├── text_cleaner.py
│   └── timestamp_generator.py
├── rag                         <-- [Phase 3 Brain / Compiled Indexes]
│   ├── auditorium
│   │   ├── index.faiss
│   │   └── index.pkl
│   └── lighting_semantics
│       ├── index.faiss
│       └── index.pkl
├── requirements.txt
├── scan_osc.py
├── setup_auditorium.py
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       ├── viewer.js
│       └── websocket_client.js
├── templates
│   ├── components
│   │   └── fixture_card.html
│   └── index.html
├── test_osc.py
├── tests
│   └── validate_phase3.py      <-- [Phase 3 Validation]
├── utils
│   ├── __init__.py
│   ├── file_io.py
│   └── osc_sender.py
├── venv/                       <-- [Python Virtual Environment]
└── visualization
    ├── __init__.py
    ├── color_utils.py
    └── playback_engine.py
```
