# PHASE 3: DUAL RAG

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 3 provides **knowledge retrieval** for the lighting decision engine. It maintains two separate knowledge bases:
1. **Auditorium KB**: Physical fixtures available (what hardware exists)
2. **Semantics KB**: Design rules (what lighting SHOULD look like for emotions/contexts)

### What Problem It Solves
Phase 4 needs to make intelligent lighting decisions, but:
- It doesn't know what fixtures are available (that's venue-specific)
- It doesn't know lighting design principles (that's domain knowledge)

Phase 3 provides both via RAG (Retrieval Augmented Generation).

### What Question It Answers
> "What fixtures can I use, and what does good lighting look like for this context?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_3/`

```
phase_3/
├── __init__.py              # Exports get_retriever
├── rag_retriever.py         # Main retriever class
├── ingestion/
│   └── knowledge_ingestion.py   # (Builds FAISS indexes)
├── knowledge/
│   ├── auditorium/
│   │   └── fixtures.json    # Source fixture data
│   └── semantics/
│       └── baseline_semantics.json  # Source design rules
├── rag/
│   ├── auditorium/
│   │   ├── index.faiss      # Vector index
│   │   └── index.pkl        # Metadata
│   └── lighting_semantics/
│       ├── index.faiss
│       └── index.pkl
└── schemas/
    ├── fixture_knowledge_schema.json
    └── lighting_semantics_knowledge_schema.json
```

---

### File: `phase_3/__init__.py`

**Why This File Exists:**
Exports the public API.

**Exports:**
- `get_retriever()` → returns singleton `Phase3Retriever`

**Who Calls It:**
- Phase 4 (LightingDecisionEngine imports retriever)
- Phase 6 (for knowledge verification)

---

### File: `phase_3/rag_retriever.py`

**Why This File Exists:**
Contains the main retriever class that provides vector similarity search over both knowledge bases.

**How It Is Used:**
Phase 4 calls `retrieve_auditorium_context()` and `retrieve_semantics_context()`.

**Dependencies:**
- `langchain_community.vectorstores.FAISS`
- `langchain_huggingface.HuggingFaceEmbeddings`

---

### Directory: `phase_3/knowledge/`

**Why This Exists:**
Source truth for knowledge. Contains raw JSON files that are ingested into FAISS.

#### `knowledge/auditorium/fixtures.json`

Contains 50+ fixture definitions following the Phase 0 `fixture_schema.json` structure.

**Sample groups defined:**
- `FOH_WASH` (Front of House wash)
- `FOH_SPOT` (Front of House spot)
- `FOH_INTELLIGENT` (Moving heads)
- `STAGE_BLINDERS`
- `STAGE_WASH_COLOR` (RGB pars)

#### `knowledge/semantics/baseline_semantics.json`

Contains lighting design rules for different contexts:
- Script types: `formal_event`, `drama`
- Emotions: `fear`, `joy`, `sadness`, `anger`
- Scene functions: `transition`

---

### Directory: `phase_3/rag/`

**Why This Exists:**
Contains pre-built FAISS vector indexes. These are NOT built at runtime.

**Files:**
- `auditorium/index.faiss`, `auditorium/index.pkl` — Fixture vectors + metadata
- `lighting_semantics/index.faiss`, `lighting_semantics/index.pkl` — Semantics vectors + metadata

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

### Class: `Phase3Retriever`

**Purpose:**
Provides vector similarity search over both knowledge bases.

**Constructor Behavior:**
```python
def __init__(self):
```
1. Initializes HuggingFace embeddings (`all-MiniLM-L6-v2`)
2. Loads auditorium FAISS index
3. Loads semantics FAISS index
4. Prints status messages

**Internal State:**
- `self.embeddings`: HuggingFaceEmbeddings model
- `self.auditorium_db`: FAISS instance (or None)
- `self.semantics_db`: FAISS instance (or None)

**Lifecycle:**
1. Singleton created via `get_retriever()`
2. Indexes are loaded once
3. Reused for all queries

**Who Instantiates It:**
- `get_retriever()` function

**Who Consumes It:**
- Phase 4 `LightingDecisionEngine`

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `Phase3Retriever.__init__()`

**Exact Responsibility:**
Initialize embeddings and load FAISS indexes.

**Side Effects:**
- Prints initialization messages
- Loads large model into memory

**Failure Modes:**
- Index not found → sets db to None, prints warning
- Index corrupt → catches exception, prints error, sets db to None

---

### `Phase3Retriever._load_index(path: str)`

**Exact Responsibility:**
Load a FAISS index from disk.

**Input Parameters:**
- `path` (str): Path to index directory

**Output Values:**
- `FAISS` instance on success
- `None` on failure

**Failure Modes:**
- Path doesn't exist → returns None
- Load error → catches exception, returns None

---

### `Phase3Retriever.retrieve_auditorium_context(query: str, k: int = 5) -> List[Dict]`

**Exact Responsibility:**
Query the fixture knowledge base.

**Input Parameters:**
- `query` (str): Natural language description (e.g., "spotlight for podium")
- `k` (int): Number of results to return

**Output Values:**
List of fixture metadata dictionaries (from `fixtures.json`)

**Failure Modes:**
- DB is None → returns empty list

**Where Called From:**
- Phase 4 `_get_auditorium_context()` (commented out in current impl)

---

### `Phase3Retriever.retrieve_semantics_context(emotion: str, script_type: str, k: int = 3) -> List[Dict]`

**Exact Responsibility:**
Query the design rules knowledge base.

**Input Parameters:**
- `emotion` (str): Primary emotion (e.g., "fear", "joy")
- `script_type` (str): Script type (e.g., "drama", "formal_event")
- `k` (int): Number of results to return

**Output Values:**
List of semantic rule metadata dictionaries (from `baseline_semantics.json`)

**Failure Modes:**
- DB is None → returns empty list

**Where Called From:**
- Phase 4 `_get_semantics_context()` (commented out in current impl)

---

### `get_retriever() -> Phase3Retriever`

**Exact Responsibility:**
Singleton factory for retriever.

**Output Values:**
`Phase3Retriever` instance

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3 EXECUTION FLOW                                         │
└─────────────────────────────────────────────────────────────────┘

1. INITIALIZATION (once per session):
   get_retriever()
   └── Phase3Retriever.__init__()
       ├── Load HuggingFace embeddings
       ├── Load auditorium FAISS index
       └── Load semantics FAISS index

2. QUERY AUDITORIUM (called by Phase 4):
   retriever.retrieve_auditorium_context("front wash for stage")
   └── FAISS similarity_search()
   └── Return fixture metadata list

3. QUERY SEMANTICS (called by Phase 4):
   retriever.retrieve_semantics_context("fear", "drama")
   └── FAISS similarity_search()
   └── Return design rule metadata list
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Fixture Metadata (from auditorium KB)
```python
{
    "fixture_id": "FOH_FRESNEL_01",
    "group_id": "FOH_WASH",
    "fixture_type": "fresnel",
    "position": {"x": -8.0, "y": 10.0, "z": 6.0},
    "capabilities": ["dim"],
    "constraints": {"max_intensity": 1.0}
}
```

### Semantics Metadata (from semantics KB)
```python
{
    "context_type": "emotion",
    "context_value": "fear",
    "priority": 0.8,
    "rules": {
        "intensity": {"preferred_range": [0.1, 0.4]},
        "color": {"temperature": "cool", "palettes": ["dark_blue", "cold_white"]},
        "transitions": {"speed": "slow"}
    }
}
```

### Available Groups in Auditorium KB
- `FOH_WASH` — Front of house wash coverage
- `FOH_SPOT` — Front of house spotlights
- `FOH_INTELLIGENT` — Moving heads
- `STAGE_BLINDERS` — High-intensity blinders
- `STAGE_WASH_COLOR` — RGB color wash

---

## 7️⃣ FAILURE BEHAVIOR

### FAISS Index Not Found
- Warning printed
- DB set to None
- Queries return empty list
- **Pipeline continues** (Phase 4 has fallback rules)

### FAISS Load Error
- Error printed
- DB set to None
- Queries return empty list
- **Pipeline continues**

### Query on None DB
- Returns empty list immediately
- No exception raised
- **Pipeline continues**

**Phase 3 is designed to degrade gracefully.**

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 3 MUST NOT Do:
- ❌ Must NOT parse scripts (that's Phase 1)
- ❌ Must NOT analyze emotions (that's Phase 2)
- ❌ Must NOT make lighting decisions (that's Phase 4)
- ❌ Must NOT translate to DMX (that's Phase 8)
- ❌ Must NOT modify knowledge at runtime

### What Phase 3 MUST Do:
- ✅ Provide fixture knowledge on request
- ✅ Provide design rule knowledge on request
- ✅ Return data in consistent format

### How Phase Isolation Is Enforced:
- Read-only access to knowledge files
- Returns metadata only (no behavior)
- No imports from other phases

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why are there two knowledge bases instead of one?"

They answer fundamentally different questions:
- **Auditorium**: "What CAN I use?" (physical reality)
- **Semantics**: "What SHOULD I use?" (design preference)

Separation allows:
- Venue changes (swap auditorium KB)
- Design style changes (swap semantics KB)

### "Why is RAG used instead of direct lookup?"

Natural language queries don't map cleanly to keys. RAG allows:
- "Give me something for dramatic tension" → finds `fear` rules
- "Front light for podium" → finds FOH fixtures

### "Why does the retriever return metadata instead of documents?"

The document content is embedded for search, but the metadata contains the structured data Phase 4 needs. Returning metadata directly avoids parsing.

### "Why are indexes pre-built instead of built at runtime?"

Building FAISS indexes is slow. Pre-building allows:
- Fast startup
- Consistent embeddings
- No runtime surprises

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 3:
1. **Consistent query interface**: Same method signatures regardless of KB contents
2. **Graceful failure**: Missing indexes don't crash the system
3. **Stateless queries**: Each query is independent
4. **Metadata format**: Returns structured dicts matching source JSON

### Invariants Maintained:
- Knowledge is read-only at runtime
- Retriever is singleton (one instance)
- Query results are deterministic for same inputs
- Empty results are valid (empty list, not None)

### What Would Break If Phase 3 Were Removed:
- Phase 4 would have no context about available fixtures
- Phase 4 would have no design guidance
- All lighting decisions would rely on hardcoded fallback rules
- System would lose venue adaptability
