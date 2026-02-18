import asyncio
import websockets
import json
import os

# CONFIGURATION
PORT = 8765
HOST = "localhost"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTRUCTIONS_PATH = os.path.join(SCRIPT_DIR, "../data/lighting_instructions.json")
SCRIPT_PATH = os.path.join(SCRIPT_DIR, "../data/raw_scripts/Script-2.txt")

# --- COLOR NAME → HEX MAPPING ---
COLOR_MAP = {
    "warm_white":   "#FFF5E1",
    "white":        "#FFFFFF",
    "warm_amber":   "#FFB347",
    "cool_blue":    "#4488FF",
    "steel_blue":   "#4682B4",
    "bright_white": "#FFFFFF",
    "deep_red":     "#FF0000",
}

# --- INSTRUCTION GROUP → FIXTURE TYPE MAPPING ---
# Maps the abstract group_ids from the JSON instructions
# to the actual fixture ID prefixes in our 3D simulation.
GROUP_TO_FIXTURES = {
    "FRONT_WASH": ["FOH_FRESNEL", "FOH_PROFILE"],       # Front-of-house wash & spot
    "BACK_LIGHT": ["STAGE_BLINDER"],                     # Back light / blinders
    "SIDE_FILL":  ["FOH_MOVING", "STAGE_RGB_PAR"],       # Side fill: movers + color PARs
}

# --- EMOTION → SMOKE MAPPING ---
SMOKE_EMOTIONS = {"fear", "anger", "surprise"}


class CueEngine:
    def __init__(self):
        self.cues = []
        self.current_index = 0
        self.is_holding = False
        self.clients = set()
        self.script_lines = []
        self.load_instructions()

    def load_instructions(self):
        """Load the JSON lighting instructions and optionally the script text."""
        try:
            with open(INSTRUCTIONS_PATH, 'r') as f:
                instructions = json.load(f)

            # Optionally load script text for display alongside cues
            try:
                with open(SCRIPT_PATH, 'r') as f:
                    self.script_lines = [l.strip() for l in f.readlines() if l.strip()]
            except:
                self.script_lines = []

            self.cues = []
            for i, scene in enumerate(instructions):
                # Convert instruction groups to our fixture format
                scene_data = self._convert_groups(scene)

                # Build display text
                meta = scene.get("metadata", {})
                emotion = meta.get("emotion", "—")
                technique = meta.get("technique", "—")
                tw = scene.get("time_window", {})
                time_str = f"{tw.get('start', 0):.0f}s – {tw.get('end', 0):.0f}s"
                duration = tw.get('end', 0) - tw.get('start', 0)

                # Get transition info
                first_group = scene.get("groups", [{}])[0]
                transition = first_group.get("transition", {})
                trans_type = transition.get("type", "fade").upper()
                trans_dur = transition.get("duration", 2.0)

                display_text = (
                    f"{scene.get('scene_id', f'scene_{i+1:03d}')} │ "
                    f"{emotion.upper()} │ {technique} │ "
                    f"⏱ {time_str} │ {trans_type} ({trans_dur}s)"
                )

                self.cues.append({
                    "id": i,
                    "text": display_text,
                    "scene": emotion.upper(),
                    "data": scene_data,
                    "duration": max(2.0, duration),   # Min 2s per cue
                    "transition_type": trans_type.lower(),
                    "transition_duration": trans_dur,
                })

            print(f"✅ Loaded {len(self.cues)} lighting cues from instructions.")
            print(f"   Script lines loaded: {len(self.script_lines)}")

        except Exception as e:
            print(f"❌ Error loading instructions: {e}")
            import traceback
            traceback.print_exc()

    def _convert_groups(self, scene):
        """Convert JSON instruction groups to our simulation's fixture format."""
        result = {}
        has_smoke = False
        emotion = scene.get("metadata", {}).get("emotion", "neutral")

        for group in scene.get("groups", []):
            group_id = group.get("group_id", "")
            params = group.get("parameters", {})

            # Get intensity (0-1 → 0-100)
            intensity = round(params.get("intensity", 0) * 100)

            # Resolve color name to hex
            color_name = params.get("color", "white")
            color_hex = COLOR_MAP.get(color_name, "#FFFFFF")

            # Map to simulation fixture keys
            fixture_prefixes = GROUP_TO_FIXTURES.get(group_id, [])
            for prefix in fixture_prefixes:
                result[prefix] = {
                    "intensity": intensity,
                    "color": color_hex,
                }

        # Determine smoke based on emotion
        if emotion in SMOKE_EMOTIONS:
            has_smoke = True

        result["SMOKE"] = has_smoke
        return result

    def get_state(self):
        """Build state payload for the frontend."""
        idx = self.current_index
        total = len(self.cues)

        # Context window: prev 3, current, next 4
        context = []
        for i in range(max(0, idx - 3), min(total, idx + 5)):
            cue = self.cues[i].copy()
            cue['active'] = (i == idx)
            # Remove heavy data from context (frontend doesn't need it for list display)
            cue.pop('data', None)
            context.append(cue)

        curr_cue = self.cues[idx] if 0 <= idx < total else None

        return {
            "type": "state_update",
            "is_holding": self.is_holding,
            "current_index": idx,
            "total_cues": total,
            "context_window": context,
            "scene_data": curr_cue["data"] if curr_cue else None,
            "transition_type": curr_cue.get("transition_type", "fade") if curr_cue else "fade",
            "transition_duration": curr_cue.get("transition_duration", 2.0) if curr_cue else 2.0,
        }

    def next_cue(self):
        if self.current_index < len(self.cues) - 1:
            self.current_index += 1
            cue = self.cues[self.current_index]
            print(f"  ▶ Cue {self.current_index}: {cue['scene']} ({cue['transition_type']})")
            return True
        return False

    def prev_cue(self):
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False


engine = CueEngine()


async def handler(websocket):
    engine.clients.add(websocket)
    try:
        # Send initial state immediately
        await websocket.send(json.dumps(engine.get_state()))

        async for message in websocket:
            msg = json.loads(message)
            cmd = msg.get("command")

            changed = False
            if cmd == "NEXT":
                changed = engine.next_cue()
            elif cmd == "PREV":
                changed = engine.prev_cue()
            elif cmd == "JUMP":
                idx = msg.get("index")
                if idx is not None and 0 <= idx < len(engine.cues):
                    engine.current_index = idx
                    changed = True
            elif cmd == "HOLD":
                engine.is_holding = not engine.is_holding
                status = "⏸ HOLDING" if engine.is_holding else "▶ RESUMED"
                print(f"  {status}")
                changed = True

            if changed:
                state = json.dumps(engine.get_state())
                for client in list(engine.clients):
                    try:
                        await client.send(state)
                    except:
                        engine.clients.discard(client)

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        engine.clients.discard(websocket)


async def auto_runner():
    """Auto-advance cues based on their time_window durations."""
    while True:
        if not engine.is_holding and engine.current_index < len(engine.cues) - 1:
            curr = engine.cues[engine.current_index]
            duration = curr.get("duration", 3.0)

            await asyncio.sleep(duration)

            # Double-check hold state after sleep
            if not engine.is_holding:
                if engine.next_cue():
                    state = json.dumps(engine.get_state())
                    for client in list(engine.clients):
                        try:
                            await client.send(state)
                        except:
                            engine.clients.discard(client)
        else:
            await asyncio.sleep(0.5)


async def main():
    async with websockets.serve(handler, HOST, PORT):
        print(f"🎭 Lighting Console running on ws://{HOST}:{PORT}")
        print(f"   {len(engine.cues)} cues loaded. Auto-advancing by time_window duration.")
        print(f"   Open http://localhost:8081 to view simulation.\n")
        await auto_runner()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopping Console...")
