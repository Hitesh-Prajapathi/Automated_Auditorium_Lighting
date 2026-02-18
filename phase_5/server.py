"""
Phase 5 Server — External Simulation Launcher

Replaces the old embedded FastAPI + Three.js server.
Now launches the External Simulation Prototype as the visualization backend.

Workflow:
1. Receives LightingInstruction list from Phase 4 / Phase 6.
2. Exports instructions to the JSON file the prototype expects.
3. Starts the prototype's WebSocket backend (test_controller.py) on port 8765.
4. Starts a static HTTP file server for the prototype's frontend on port 8081.
5. User opens http://localhost:8081 to see the 3D simulation.
"""

import os
import sys
import json
import time
import signal
import subprocess
import http.server
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional

from .threejs_adapter import InstructionExporter

# --- Path Configuration ---
# All paths are computed relative to this file's location.
PHASE_5_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = PHASE_5_DIR.parent.resolve()

# External prototype paths (NEVER MODIFIED, only read)
PROTOTYPE_DIR = PROJECT_ROOT / "external_prototype" / "external_simulation_prototype"
CONTROLLER_SCRIPT = PROTOTYPE_DIR / "test_controller.py"
FRONTEND_DIR = PROTOTYPE_DIR / "module_1"

# Data output path (the JSON file test_controller.py reads)
# test_controller.py: INSTRUCTIONS_PATH = os.path.join(SCRIPT_DIR, "../data/lighting_instructions.json")
# SCRIPT_DIR = external_simulation_prototype/ → so it reads from external_prototype/data/
DATA_OUTPUT_DIR = PROJECT_ROOT / "external_prototype" / "data"
INSTRUCTIONS_JSON_PATH = DATA_OUTPUT_DIR / "lighting_instructions.json"

# Ports
WEBSOCKET_PORT = 8765
HTTP_PORT = 8081

# --- Demo Data (Fallback) - Script-1 Horror Drama, 10 scenes ---
# Every scene uses all 3 groups: front_wash, back_light, side_fill
# side_fill → SIDE_FILL → FOH_MOVING + STAGE_RGB_PAR (the RGB fixtures)
DEMO_DATA = [
    {
        "scene_id": "scene_001",
        "time_window": {"start": 0, "end": 4},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.0, "color": "warm_white"}, "transition": {"type": "fade", "duration": 3.0}},
            {"group_id": "back_light", "parameters": {"intensity": 0.0, "color": "warm_white"}, "transition": {"type": "fade", "duration": 3.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.0, "color": "warm_white"}, "transition": {"type": "fade", "duration": 3.0}},
        ],
        "metadata": {"emotion": "neutral", "technique": "FADE IN - blackout"}
    },
    {
        "scene_id": "scene_002",
        "time_window": {"start": 4, "end": 33},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.4, "color": "warm_amber"}, "transition": {"type": "fade", "duration": 3.0}},
            {"group_id": "back_light", "parameters": {"intensity": 0.2, "color": "warm_white"}, "transition": {"type": "fade", "duration": 3.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.3, "color": "warm_amber"}, "transition": {"type": "fade", "duration": 3.0}},
        ],
        "metadata": {"emotion": "neutral", "technique": "Dim warm interior - living room night"}
    },
    {
        "scene_id": "scene_003",
        "time_window": {"start": 35, "end": 37},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.3, "color": "warm_amber"}, "transition": {"type": "fade", "duration": 0.5}},
            {"group_id": "back_light", "parameters": {"intensity": 0.1, "color": "warm_white"}, "transition": {"type": "fade", "duration": 0.5}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.2, "color": "warm_amber"}, "transition": {"type": "fade", "duration": 0.5}},
        ],
        "metadata": {"emotion": "neutral", "technique": "CUT TO - brief transition"}
    },
    {
        "scene_id": "scene_004",
        "time_window": {"start": 39, "end": 52},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.3, "color": "warm_amber"}, "transition": {"type": "fade", "duration": 2.0}},
            {"group_id": "back_light", "parameters": {"intensity": 0.4, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 2.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.5, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 2.0}},
        ],
        "metadata": {"emotion": "fear", "technique": "Kitchen whisper - cold creeping in"}
    },
    {
        "scene_id": "scene_005",
        "time_window": {"start": 54, "end": 80},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.5, "color": "warm_white"}, "transition": {"type": "fade", "duration": 2.0}},
            {"group_id": "back_light", "parameters": {"intensity": 0.3, "color": "steel_blue"}, "transition": {"type": "fade", "duration": 2.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.6, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 3.0}},
        ],
        "metadata": {"emotion": "surprise", "technique": "Hallway - Lily disappears"}
    },
    {
        "scene_id": "scene_006",
        "time_window": {"start": 82, "end": 108},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.6, "color": "warm_white"}, "transition": {"type": "fade", "duration": 1.5}},
            {"group_id": "back_light", "parameters": {"intensity": 0.7, "color": "deep_red"}, "transition": {"type": "fade", "duration": 2.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.8, "color": "deep_red"}, "transition": {"type": "fade", "duration": 2.0}},
        ],
        "metadata": {"emotion": "fear", "technique": "Living room panic - red danger wash"}
    },
    {
        "scene_id": "scene_007",
        "time_window": {"start": 110, "end": 112},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.1, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 0.3}},
            {"group_id": "back_light", "parameters": {"intensity": 0.1, "color": "steel_blue"}, "transition": {"type": "fade", "duration": 0.3}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.1, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 0.3}},
        ],
        "metadata": {"emotion": "neutral", "technique": "CUT TO - near blackout"}
    },
    {
        "scene_id": "scene_008",
        "time_window": {"start": 114, "end": 144},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.2, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 3.0}},
            {"group_id": "back_light", "parameters": {"intensity": 0.5, "color": "steel_blue"}, "transition": {"type": "fade", "duration": 3.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.7, "color": "cool_blue"}, "transition": {"type": "fade", "duration": 3.0}},
        ],
        "metadata": {"emotion": "fear", "technique": "Basement descent - deep cold blue"}
    },
    {
        "scene_id": "scene_009",
        "time_window": {"start": 146, "end": 165},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.8, "color": "bright_white"}, "transition": {"type": "fade", "duration": 0.5}},
            {"group_id": "back_light", "parameters": {"intensity": 1.0, "color": "deep_red"}, "transition": {"type": "fade", "duration": 1.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 1.0, "color": "deep_red"}, "transition": {"type": "fade", "duration": 1.0}},
        ],
        "metadata": {"emotion": "fear", "technique": "Mirror smash climax - FULL RED BLAST"}
    },
    {
        "scene_id": "scene_010",
        "time_window": {"start": 167, "end": 172},
        "groups": [
            {"group_id": "front_wash", "parameters": {"intensity": 0.0, "color": "warm_white"}, "transition": {"type": "fade", "duration": 4.0}},
            {"group_id": "back_light", "parameters": {"intensity": 0.0, "color": "warm_white"}, "transition": {"type": "fade", "duration": 4.0}},
            {"group_id": "side_fill", "parameters": {"intensity": 0.0, "color": "warm_white"}, "transition": {"type": "fade", "duration": 4.0}},
        ],
        "metadata": {"emotion": "neutral", "technique": "FADE OUT - total blackout"}
    },
]


class SimulationLauncher:
    """
    Manages the lifecycle of the external simulation processes.
    """

    def __init__(self):
        self.exporter = InstructionExporter()
        self._controller_process: Optional[subprocess.Popen] = None
        self._http_thread: Optional[threading.Thread] = None
        self._http_server: Optional[http.server.HTTPServer] = None

    def _export_instructions(self, instructions: List[Dict[str, Any]]) -> str:
        """Export instructions to the JSON file the prototype expects."""
        filepath = str(INSTRUCTIONS_JSON_PATH)
        self.exporter.export_to_json(instructions, filepath)
        print(f"  📝 Exported {len(instructions)} instructions to {filepath}")
        return filepath

    def _start_controller(self) -> subprocess.Popen:
        """Start the external prototype's WebSocket backend."""
        if not CONTROLLER_SCRIPT.exists():
            raise FileNotFoundError(
                f"External simulation controller not found: {CONTROLLER_SCRIPT}\n"
                f"Please ensure the external_simulation_prototype is extracted in external_prototype/"
            )

        # Use the same Python interpreter that's running this script
        python_exe = sys.executable

        proc = subprocess.Popen(
            [python_exe, str(CONTROLLER_SCRIPT)],
            cwd=str(PROTOTYPE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Give it a moment to start
        time.sleep(1.5)

        # Check it didn't crash immediately
        if proc.poll() is not None:
            output = proc.stdout.read() if proc.stdout else ""
            raise RuntimeError(
                f"Controller process exited immediately with code {proc.returncode}.\n"
                f"Output: {output}"
            )

        print(f"  🎭 WebSocket controller started on ws://localhost:{WEBSOCKET_PORT} (PID: {proc.pid})")
        return proc

    def _start_http_server(self) -> None:
        """Start a simple HTTP file server for the frontend."""
        if not FRONTEND_DIR.exists():
            raise FileNotFoundError(
                f"External simulation frontend not found: {FRONTEND_DIR}\n"
                f"Please ensure the external_simulation_prototype/module_1/ exists."
            )

        handler = http.server.SimpleHTTPRequestHandler

        class QuietHandler(handler):
            """Suppress request logging."""
            def log_message(self, format, *args):
                pass  # Silence

        os.chdir(str(FRONTEND_DIR))
        self._http_server = http.server.HTTPServer(("", HTTP_PORT), QuietHandler)

        self._http_thread = threading.Thread(
            target=self._http_server.serve_forever,
            daemon=True
        )
        self._http_thread.start()
        print(f"  🌐 Frontend served at http://localhost:{HTTP_PORT}")

    def launch(self, instructions: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Launch the full simulation.

        Args:
            instructions: List of LightingInstruction dicts from Phase 4.
                          Falls back to DEMO_DATA if None.
        """
        if instructions is None:
            print("  ⚠️  No instructions provided, using demo data.")
            instructions = DEMO_DATA

        print("\n" + "=" * 60)
        print("  PHASE 5: EXTERNAL SIMULATION LAUNCHER")
        print("=" * 60)

        # Step 1: Export instructions
        self._export_instructions(instructions)

        # Step 2: Start WebSocket backend
        self._controller_process = self._start_controller()

        # Step 3: Start HTTP frontend server
        self._start_http_server()

        print("\n" + "-" * 60)
        print(f"  ✅ Simulation is LIVE!")
        print(f"  🔗 Open: http://localhost:{HTTP_PORT}")
        print(f"  Press Ctrl+C to stop.")
        print("-" * 60 + "\n")

    def stop(self) -> None:
        """Stop all simulation processes."""
        print("\n  🛑 Stopping simulation...")

        if self._http_server:
            self._http_server.shutdown()
            print("    HTTP server stopped.")

        if self._controller_process and self._controller_process.poll() is None:
            self._controller_process.terminate()
            try:
                self._controller_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._controller_process.kill()
            print("    WebSocket controller stopped.")

        print("  ✅ Simulation stopped.\n")

    def run_blocking(self, instructions: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Launch and block until Ctrl+C.
        This is the typical entry point for standalone usage.
        """
        self.launch(instructions)

        try:
            # Keep main thread alive until Ctrl+C
            while True:
                # Also forward controller output to console
                if self._controller_process and self._controller_process.stdout:
                    line = self._controller_process.stdout.readline()
                    if line:
                        print(f"  [CTRL] {line.rstrip()}")

                    # Check if controller died
                    if self._controller_process.poll() is not None:
                        print("  ⚠️  Controller process exited unexpectedly.")
                        break
                else:
                    time.sleep(0.5)

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


def launch_simulation(instructions: Optional[List[Dict[str, Any]]] = None) -> SimulationLauncher:
    """
    Public API for Phase 5.
    Launches the external simulation with the given instructions.

    Args:
        instructions: List of LightingInstruction dicts from Phase 4 output.
                      Falls back to demo data if None.

    Returns:
        SimulationLauncher instance (call .stop() to shut down).
    """
    launcher = SimulationLauncher()
    launcher.launch(instructions)
    return launcher


# --- Standalone Entry Point ---
if __name__ == "__main__":
    launcher = SimulationLauncher()
    launcher.run_blocking()
