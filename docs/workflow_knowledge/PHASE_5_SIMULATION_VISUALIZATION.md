# PHASE 5: SIMULATION & VISUALIZATION

## 1️⃣ PHASE PURPOSE

### What This Phase Exists For
Phase 5 provides **visual feedback** of lighting decisions. It renders `LightingInstruction` objects into a 3D simulation that can be viewed in a browser.

### What Problem It Solves
Before sending lighting to real hardware (Phase 8), designers need to:
- Preview what scenes will look like
- Verify timing and transitions
- Debug lighting decisions

Phase 5 provides this preview without touching hardware.

### What Question It Answers
> "What does this lighting look like on stage?"

---

## 2️⃣ DIRECTORY & FILE BREAKDOWN

### Directory: `phase_5/`

```
phase_5/
├── __init__.py          # Module exports
├── README.md            # Phase documentation
├── IMPLEMENTATION_PLAN.md
├── color_utils.py       # Color name to RGB conversion
├── playback_engine.py   # Timing and playback control
├── scene_renderer.py    # Maintains current lighting state
├── threejs_adapter.py   # Converts to Three.js format
├── server.py            # WebSocket server for live preview
└── static/
    └── index.html       # Browser frontend
```

---

### File: `phase_5/__init__.py`

**Exports:**
- `color_utils` module
- `playback_engine` module

---

### File: `phase_5/color_utils.py`

**Why This File Exists:**
Converts semantic color names (from Phase 4) to RGB values for rendering.

**Key Functions:**
- `semantic_to_rgb(color_name)` → (r, g, b) tuple
- `hex_to_rgb(hex_string)` → (r, g, b) tuple
- `blend_colors(color1, color2, ratio)` → blended RGB

---

### File: `phase_5/playback_engine.py`

**Why This File Exists:**
Controls timing and playback of lighting sequences.

**Key Class:** `PlaybackEngine`
- Manages play/pause/stop/seek
- Tracks elapsed time
- Updates `SceneRenderer` at each frame

---

### File: `phase_5/scene_renderer.py`

**Why This File Exists:**
Maintains the current visual state of all light groups.

**Key Class:** `SceneRenderer`
- Stores current intensity/color/focus for each group
- Applies transitions over time
- Provides state snapshot for rendering

---

### File: `phase_5/threejs_adapter.py`

**Why This File Exists:**
Converts `SceneRenderer` state to Three.js-compatible format.

**Key Class:** `ThreeJSAdapter`
- Maps group IDs to virtual 3D positions
- Generates light array for frontend

---

### File: `phase_5/server.py`

**Why This File Exists:**
WebSocket server that streams lighting state to browser.

**Key Functions:**
- Serves `static/index.html`
- Streams lighting updates via WebSocket
- Handles play/pause commands from frontend

---

### File: `phase_5/static/index.html`

**Why This File Exists:**
Browser-based 3D visualization using Three.js.

**Functionality:**
- Receives WebSocket updates
- Renders 3D light representations
- Provides playback controls

---

## 3️⃣ CLASS-BY-CLASS ANALYSIS

### Class: `PlaybackEngine`

**Purpose:**
Controls timing and applies `LightingInstruction` to renderer.

**Constructor:**
```python
def __init__(self, renderer: SceneRenderer):
```

**Internal State:**
- `self.renderer`: SceneRenderer instance
- `self.instructions`: List of LightingInstruction
- `self.current_time`: Elapsed time in seconds
- `self.is_playing`: Play state
- `self.current_instruction_index`: Active instruction

**Key Methods:**
- `load_instructions(instructions)`: Load sequence
- `play()`: Start playback
- `pause()`: Pause playback
- `stop()`: Reset to beginning
- `seek(time)`: Jump to specific time
- `tick(delta_time)`: Advance by delta, update renderer

---

### Class: `SceneRenderer`

**Purpose:**
Maintains current lighting state for all groups.

**Constructor:**
```python
def __init__(self):
```

**Internal State:**
```python
self.group_states = {
    "group_id": {
        "intensity": float,
        "color": str,
        "focus_area": str
    }
}
```

**Key Methods:**
- `update_group(group_id, parameters)`: Apply new values
- `get_state()`: Return current states
- `reset()`: Clear all states

---

### Class: `ThreeJSAdapter`

**Purpose:**
Converts renderer state to Three.js format.

**Constructor:**
```python
def __init__(self, renderer: SceneRenderer):
```

**Key Methods:**
- `get_lights()`: Returns list of light objects for frontend

**Output Format:**
```python
[
    {
        "id": "front_wash",
        "position": {"x": 0, "y": 5, "z": 10},
        "color": "#ff9900",
        "intensity": 0.8
    }
]
```

---

## 4️⃣ FUNCTION-BY-FUNCTION ANALYSIS

### `color_utils.semantic_to_rgb(color_name: str) -> tuple`

**Exact Responsibility:**
Map semantic color names to RGB tuples.

**Mappings Include:**
- `warm_amber` → (255, 191, 0)
- `cool_blue` → (0, 100, 200)
- `dark_blue` → (0, 0, 139)
- `red` → (255, 0, 0)
- `natural_white` → (255, 255, 255)

**Failure Modes:**
- Unknown color → returns white (255, 255, 255)

---

### `PlaybackEngine.tick(delta_time: float)`

**Exact Responsibility:**
Advance playback by delta_time seconds.

**Implementation:**
1. Add delta to `current_time`
2. Find active instruction for current_time
3. Apply instruction to renderer (considering transitions)

---

### `SceneRenderer.update_group(group_id, parameters)`

**Exact Responsibility:**
Update a single group's state.

**Input:** Group ID and parameters dict

---

### `ThreeJSAdapter.get_lights() -> list`

**Exact Responsibility:**
Generate Three.js-compatible light definitions.

**Implementation:**
1. Get current state from renderer
2. Map each group to a position (illustrative, not real)
3. Convert color names to hex
4. Return light array

---

## 5️⃣ EXECUTION FLOW

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 5 EXECUTION FLOW                                         │
└─────────────────────────────────────────────────────────────────┘

1. LOAD:
   PlaybackEngine.load_instructions([LightingInstruction, ...])
          │
          ▼
2. PLAY:
   PlaybackEngine.play()
   └── Starts internal timer
          │
          ▼
3. TICK LOOP (every frame):
   PlaybackEngine.tick(delta_time)
   ├── Advance current_time
   ├── Find active instruction
   └── SceneRenderer.update_group(...)
          │
          ▼
4. RENDER:
   ThreeJSAdapter.get_lights()
   └── Returns Three.js light array
          │
          ▼
5. OUTPUT:
   WebSocket → Browser → Three.js Visualization
```

---

## 6️⃣ DATA STRUCTURES & MODELS

### Input: LightingInstruction (from Phase 4)
```python
{
    "scene_id": str,
    "time_window": {"start": float, "end": float},
    "groups": [
        {
            "group_id": str,
            "parameters": {
                "intensity": float,
                "color": str,
                "focus_area": str
            },
            "transition": {
                "type": str,
                "duration": float
            }
        }
    ]
}
```

### Output: Three.js Light Object
```python
{
    "id": str,
    "position": {"x": float, "y": float, "z": float},
    "color": str,  # hex color
    "intensity": float
}
```

---

## 7️⃣ FAILURE BEHAVIOR

### Unknown Color Name
- Returns white
- **Visualization continues**

### Missing Group in State
- Creates new group entry
- **Visualization continues**

### WebSocket Disconnect
- Server logs warning
- **Playback continues** (reconnect possible)

---

## 8️⃣ PHASE BOUNDARIES

### What Phase 5 MUST NOT Do:
- ❌ Must NOT send DMX/OSC/MIDI (that's Phase 8)
- ❌ Must NOT modify LightingInstructions
- ❌ Must NOT make lighting decisions (that's Phase 4)
- ❌ Must NOT persist state

### What Phase 5 MUST Do:
- ✅ Visualize LightingInstructions accurately
- ✅ Handle transitions correctly
- ✅ Provide real-time preview

### Principle: VISUALIZATION ≠ REALITY
Phase 5 shows what lighting **might** look like.
Phase 8 controls what lighting **actually** is.

---

## 9️⃣ COMMON CONFUSION CLARIFICATION

### "Why are group positions generated instead of from Phase 3?"

Visualization positions are **illustrative**, not exact.
Real fixture positions are in Phase 3, but Phase 5 uses simplified positions for preview.

### "Why is there no validation of LightingInstruction?"

Phase 6 validates before passing to Phase 5.
Phase 5 trusts input is valid.

### "Why WebSocket instead of HTTP polling?"

Real-time updates require push protocol.
HTTP polling would be too slow for smooth playback.

---

## 🔟 SUMMARY & GUARANTEES

### Guarantees Provided by Phase 5:
1. **Real-time preview**: Updates as fast as frame rate allows
2. **Graceful degradation**: Unknown colors → white
3. **Timing accuracy**: Transitions applied correctly

### Invariants Maintained:
- Group states always have intensity/color/focus
- Playback state is deterministic for same input
- Rendering is idempotent (same state → same output)

### What Would Break If Phase 5 Were Removed:
- No visual feedback for designers
- No way to preview before hardware execution
- Debugging lighting decisions becomes harder
