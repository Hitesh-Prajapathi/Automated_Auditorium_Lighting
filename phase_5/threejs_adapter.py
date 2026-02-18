"""
Instruction Exporter (Replaces ThreeJSAdapter)
Translates the main system's LightingInstruction format into the JSON format
expected by the External Simulation Prototype's test_controller.py.

The external prototype expects:
[
    {
        "scene_id": "scene_001",
        "time_window": {"start": 0.0, "end": 5.0},
        "groups": [
            {
                "group_id": "FRONT_WASH",
                "parameters": {"intensity": 0.8, "color": "warm_white"},
                "transition": {"type": "fade", "duration": 2.0}
            }
        ],
        "metadata": {"emotion": "joy", "technique": "warm wash"}
    }
]
"""

import json
from typing import Dict, List, Any
from .color_utils import get_hex_from_semantic

# --- Group ID Translation ---
# Main system uses lowercase snake_case; external prototype uses UPPER_SNAKE_CASE.
# The external prototype's test_controller.py maps these to fixture prefixes:
#   FRONT_WASH -> FOH_FRESNEL, FOH_PROFILE
#   BACK_LIGHT -> STAGE_BLINDER
#   SIDE_FILL  -> FOH_MOVING, STAGE_RGB_PAR
GROUP_ID_MAP = {
    "front_wash":   "FRONT_WASH",
    "back_light":   "BACK_LIGHT",
    "side_left":    "SIDE_FILL",
    "side_right":   "SIDE_FILL",
    "side_fill":    "SIDE_FILL",
    "center_spot":  "FRONT_WASH",
    "specials":     "FRONT_WASH",
    "house_lights": "FRONT_WASH",
    "ambient":      "FRONT_WASH",
    "overhead_wash": "BACK_LIGHT",
    "haze":         "SIDE_FILL",
}

# --- Color Name Translation ---
# The external prototype's test_controller.py has its own COLOR_MAP:
#   warm_white -> #FFF5E1, white -> #FFFFFF, warm_amber -> #FFB347,
#   cool_blue  -> #4488FF, steel_blue -> #4682B4, bright_white -> #FFFFFF,
#   deep_red   -> #FF0000
# We map our semantic names to the names the prototype understands.
COLOR_NAME_MAP = {
    "warm_white":     "warm_white",
    "cool_white":     "white",
    "neutral_white":  "bright_white",
    "warm_amber":     "warm_amber",
    "amber":          "warm_amber",
    "candlelight":    "warm_amber",
    "red":            "deep_red",
    "blue":           "cool_blue",
    "cool_blue":      "cool_blue",
    "night_blue":     "steel_blue",
    "white":          "white",
    "black":          "white",  # black maps to off (intensity=0 handles it)
    "off":            "white",
}


class InstructionExporter:
    """
    Converts the main system's LightingInstruction list into the JSON array
    expected by the external simulation prototype's test_controller.py.
    """

    def translate_group_id(self, group_id: str) -> str:
        """Map main system group_id to prototype group_id."""
        return GROUP_ID_MAP.get(group_id, "FRONT_WASH")

    def translate_color(self, color_semantic: str) -> str:
        """Map main system semantic color to prototype color name."""
        if not color_semantic:
            return "white"
        key = color_semantic.lower().replace(" ", "_")
        return COLOR_NAME_MAP.get(key, "white")

    def export(self, instructions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert a list of LightingInstruction dicts from the main system
        into the format expected by the external prototype.

        Args:
            instructions: List of LightingInstruction dicts from Phase 4 output.

        Returns:
            List of dicts in the external prototype's expected format.
        """
        exported = []

        for idx, inst in enumerate(instructions):
            scene_id = inst.get("scene_id", f"scene_{idx + 1:03d}")

            # Time window
            time_window = inst.get("time_window", {})
            if not time_window:
                # Generate default time windows if missing
                time_window = {
                    "start": float(idx * 5),
                    "end": float((idx + 1) * 5)
                }

            # Groups
            translated_groups = []
            for group_data in inst.get("groups", []):
                group_id = group_data.get("group_id", "front_wash")
                params = group_data.get("parameters", {})
                transition = group_data.get("transition", {"type": "fade", "duration": 2.0})

                translated_groups.append({
                    "group_id": self.translate_group_id(group_id),
                    "parameters": {
                        "intensity": params.get("intensity", 0.0),
                        "color": self.translate_color(params.get("color", "white")),
                    },
                    "transition": transition
                })

            # Metadata
            metadata = inst.get("metadata", {})
            if not metadata:
                metadata = {
                    "emotion": "neutral",
                    "technique": "general"
                }

            exported.append({
                "scene_id": scene_id,
                "time_window": time_window,
                "groups": translated_groups,
                "metadata": metadata
            })

        return exported

    def export_to_json(self, instructions: List[Dict[str, Any]], filepath: str) -> str:
        """
        Export instructions to a JSON file at the given path.

        Args:
            instructions: List of LightingInstruction dicts.
            filepath: Absolute path to write the JSON file.

        Returns:
            The filepath written to.
        """
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        exported = self.export(instructions)

        with open(filepath, 'w') as f:
            json.dump(exported, f, indent=4)

        return filepath
