# ANTIGRAVITY KNOWLEDGE BASE

**Project:** Automated Auditorium Lighting with Generative AI  
**Status:** Architecture LOCKED

---

## 1️⃣ SYSTEM PHILOSOPHY (NON-NEGOTIABLE)

- **Intent ≠ Execution**
- **Knowledge ≠ Decisions**
- **Contracts ≠ Logic**
- **Compatibility ≠ Correctness**

> If something "works" but violates these, it is **wrong**.

---

## 2️⃣ PHASE MODEL (AUTHORITATIVE)

The system is divided into nine strictly separated phases:

| Phase | Name          | Responsibility              |
|-------|---------------|-----------------------------|
| 0     | Contracts     | System-wide data truth      |
| 1     | Parsing       | Script → Scene structure    |
| 2     | Emotion       | Optional semantic signal    |
| 3     | Knowledge     | Facts & design bias (RAG)   |
| 4     | Decision      | Lighting intent (LLM)       |
| 5     | Simulation    | Visual execution            |
| 6     | Orchestration | Pipeline control            |
| 7     | Evaluation    | Logging & metrics           |
| 8     | Hardware      | Real-world control          |

> **No phase may absorb another phase's responsibility.**

---

## 3️⃣ PHASE 0 — CONTRACTS (SYSTEM TRUTH)

### Purpose
Define data shape only, never behavior.

### Canonical Contract Files
Exactly four files exist:
1. `scene_schema.json`
2. `fixture_schema.json`
3. `lighting_instruction_schema.json`
4. `lighting_semantics_schema.json`

### Contract Rules
- Must be **DMX-free**
- Must be **group-level**
- Must be **hardware-agnostic**
- Must **not encode logic**

> If a field answers "how", it is not a contract.

---

## 4️⃣ PHASE 1 & 2 — STRUCTURE & SIGNAL

- Phase 1 produces deterministic Scene JSON
- Phase 2 may enrich with emotion
- Emotion is **OPTIONAL** and nullable
- **No lighting decisions occur here**

---

## 5️⃣ PHASE 3 — KNOWLEDGE & RAG

### Two Independent RAGs (Never Mixed)

#### RAG 1: Auditorium Knowledge
**Answers:** "What exists physically?"

**Contains:**
- Fixtures
- Groups
- Positions
- Capabilities

**Contains NO:**
- Emotion
- Lighting intent
- DMX

#### RAG 2: Lighting Semantics
**Answers:** "What usually feels appropriate?"

**Contains:**
- Emotion-based tendencies
- Script-type tendencies
- Ranges, not commands

**Contains NO:**
- Fixtures
- DMX
- Absolute rules

### RAG Invariants
- RAG artifacts are **read-only**
- RAGs are queried **separately**
- Phase 3 **never decides anything**

---

## 6️⃣ PHASE 4 — DECISION ENGINE

### Purpose
Convert: **Scene + Knowledge → Lighting Intent**

### Output Rules
- **Group-level only**
- **Semantic parameters only**
- **DMX-free**
- **Executable without reasoning**

> Reasoning, if present, is metadata only.

---

## 7️⃣ PHASE 5 — SIMULATION

- Converts intent → visuals
- **No AI**
- **No logic**
- **No decisions**

---

## 8️⃣ PHASE 6 — ORCHESTRATION

- Controls execution order
- Handles batching & state
- **Does not change intent**

---

## 9️⃣ PHASE 7 — EVALUATION

- Logging
- Metrics
- Traceability
- Paper support

---

## 🔌 PHASE 8 — HARDWARE AUTOMATION

### Purpose
Convert intent → real-world signals

### Allowed here ONLY:
- DMX
- OSC
- MIDI
- Patch maps
- Hardware executors

> **Hardware must never appear earlier.**

---

## 10️⃣ FORBIDDEN CONCEPTS (GLOBAL)

These must be **removed if found outside Phase 8**:
- DMX channels
- Universes
- Patch sheets
- Cue schemas
- Fixture-level execution
- Hardware addresses

---

## 11️⃣ CONFLICT RESOLUTION HEURISTIC

If unsure where a file belongs, ask:

| Question                        | Phase |
|---------------------------------|-------|
| Does it define shape?           | 0     |
| Does it structure text?         | 1     |
| Does it extract meaning?        | 2     |
| Does it know facts?             | 3     |
| Does it decide intent?          | 4     |
| Does it render?                 | 5     |
| Does it coordinate?             | 6     |
| Does it measure?                | 7     |
| Does it drive hardware?         | 8     |

> If none apply → **delete the file**.

---

## 12️⃣ MERGE AUTHORITY RULES

When conflicts occur:
1. Prefer **intent-level** over execution-level
2. Prefer **group-level** over fixture-level
3. Prefer **semantic** over hardware-specific
4. Prefer **architecture compliance** over convenience

---

## 13️⃣ FINAL GUARANTEE

If this knowledge base is followed:
- ✅ No merge conflicts
- ✅ No architectural drift
- ✅ No phase leakage
- ✅ Clean demo path
- ✅ Clean research narrative

---

## 📌 REMEMBER

> **You are enforcing architecture, not inventing it.**

> **This knowledge base must be treated as immutable truth during the merge.**
